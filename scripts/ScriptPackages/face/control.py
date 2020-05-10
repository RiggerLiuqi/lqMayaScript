import json
import os

import pymel.core as pm

ROOT = os.path.abspath(os.path.join(__file__+"../.."))


def get_selected_curves():
    selected = pm.selected(o=1, type="transform")
    if not len(selected):
        pm.warning("you should select curve")
        return []
    curves = []
    for curve in selected:
        curve_shape = curve.getShape()
        if not curve_shape:
            continue
        if curve_shape.type() != "nurbsCurve":
            continue
        curves.append(curve)
    if not curves:
        pm.warning("you should select curve")
        return []
    return curves


def get_selected_curve():
    curves = get_selected_curves()
    if len(curves) != 1:
        return pm.warning("you should select curve")
    return curves[0]


def get_curve_shape_points(shape):
    points = pm.xform(shape.cv, q=1, t=1)
    return [points[i: i+3] for i in range(0, len(points), 3)]


def set_curve_shape_points(shape, points):
    for i, point in enumerate(points):
        pm.xform(shape.cv[i], t=point)


def get_curve_data(curve):
    return [dict(points=get_curve_shape_points(shape),
                 degree=shape.degree(),
                 periodic=curve.form() == 3,
                 knot=shape.getKnots())
            for shape in curve.getShapes()]


def control_upload(curve=None, n=None, f=True):
    if curve is None:
        curve = get_selected_curve()
    if curve is None:
        return
    if n is None:
        n = curve.name().split("|")[-1].split(":")[0]
    path = os.path.join(ROOT, "controls", n+".json")
    if os.path.isfile(path) and not f:
        return
    with open(path, "w") as write:
        write.write(json.dumps(get_curve_data(curve), indent=4))


def set_curve_shape_scale(shape, scale):
    points = get_curve_shape_points(shape)
    points = [[xyz*scale for xyz in point] for point in points]
    set_curve_shape_points(shape, points)


def set_curve_radius(curve=None, radius=None):
    if curve is None:
        curve = get_selected_curve()
    if curve is None:
        return
    if radius is None:
        radius = pm.softSelect(q=1, ssd=1)
    scale = radius/max([sum([xyz**2 for xyz in point])**0.5 for shape in curve.getShapes()
                        for point in get_curve_shape_points(shape)])
    for shape in curve.getShapes():
        set_curve_shape_scale(shape, scale)


def set_curve_name(curve, n):
    if curve is None:
        curve = get_selected_curve()
    if curve is None:
        return
    curve.rename(n)
    for i, shape in enumerate(curve.getShapes()):
        if i:
            shape.rename(n+"Shape"+str(i))
        else:
            shape.rename(n + "Shape")


def set_curve_color(curve, c):
    for shape in curve.getShapes():
        shape.overrideEnabled.set(1)
        shape.overrideColor.set(c)


def set_curve_parent(curve, p):
    curve.setParent(p)
    curve.t.set(0, 0, 0)
    curve.r.set(0, 0, 0)
    curve.s.set(1, 1, 1)


def set_curve_locked(curve, l):
    for attr in l:
        curve.attr(attr).setLocked(True)
        curve.attr(attr).setKeyable(False)


def set_curve_shape(curve, s):
    path = os.path.join(ROOT, "controls", s + ".json")
    if not os.path.isfile(path):
        return
    with open(path, "r") as read:
        data = json.loads(read.read())
    pm.delete(curve.getShapes())
    for i, shape in enumerate(data):
        p = shape["points"]
        if shape["periodic"]:
            p = p + p[:shape["degree"]]
        temp = pm.curve(p=p, d=shape["degree"], periodic=shape["periodic"], k=shape["knot"])
        temp.getShape().setParent(curve, s=1, add=1)
        pm.delete(temp)
    for i, s in enumerate(curve.getShapes()):
        s.rename(s.rename(curve.name().split("|")[-1]+"Shape"))


def set_curve_offset(curve, o):
    for shape in curve.getShapes():
        points = get_curve_shape_points(shape)
        points = [[p1+p2 for p1, p2 in zip(o, p)] for p in points]
        set_curve_shape_points(shape, points)


def control_create(curve=None, s=None, n=None, p=None, r=None, c=None, l=None, o=None):
    if curve is None:
        curve = pm.circle(ch=1)[0]
    if s is not None:
        set_curve_shape(curve, s)
    if n is not None:
        set_curve_name(curve, n)
    if p is not None:
        set_curve_parent(curve, p)
    if r is not None:
        set_curve_radius(curve, r)
    if c is not None:
        set_curve_color(curve, c)
    if l is not None:
        set_curve_locked(curve, l)
    if o is not None:
        set_curve_offset(curve, o)
    return curve

