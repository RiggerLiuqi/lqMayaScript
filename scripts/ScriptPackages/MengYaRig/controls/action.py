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


def get_curve_points(curve_shape):
    points = pm.xform(curve_shape.cv, q=1, t=1)
    return [points[i: i+3] for i in range(0, len(points), 3)]


def set_curve_radius(curve_shape, radius):
    points = get_curve_points(curve_shape)
    old_radius = max([sum([xyz**2 for xyz in point])**0.5 for point in points])
    scale = radius/old_radius
    points = [[xyz*scale for xyz in point] for point in points]
    for i, point in enumerate(points):
        pm.xform(curve_shape.cv[i], t=point)


def set_select_curve_radius():
    radius = pm.softSelect(q=1, ssd=1)
    for curve in get_selected_curves():
        set_curve_radius(curve.getShape(), radius)


def upload_curve(curve):
    name = curve.name().split(":")[-1].split("|")[-1]
    curve_shape = curve.getShape()
    points = get_curve_points(curve_shape)
    with open(os.path.join(ROOT, "data", name+".json"), "w") as write:
        write.write(json.dumps(points))
    temp_curve = pm.group(em=1)
    curve_shape.copy(curve_shape, temp_curve)
    hud_names = pm.headsUpDisplay(q=1, lh=1)
    if hud_names is None:
        hud_names = []
    for hud_name in hud_names:
        pm.headsUpDisplay(hud_name, rem=True)
    camera = pm.PyNode("|persp")
    panel = "control_model_panel"
    if not pm.modelPanel(panel, ex=1):
        pm.modelPanel(panel, tearOff=True, toc=1)
    pm.mel.source('setRendererInModelPanel.mel')
    pm.mel.setRendererInModelPanel("base_OpenGL_Renderer", panel)
    pm.modelEditor(panel, e=1, manipulators=0, pm=1, gr=0, alo=0, dtx=0, nc=1, da="smoothShaded", po=["gpuCacheDisplayFilter", True], cam=camera)
    pm.setFocus(panel)
    pm.select(temp_curve)
    camera.r.set(-27.9383527296, 45, 0)
    pm.viewFit("persp", an=0)
    pm.isolateSelect(panel, state=1)
    pm.isolateSelect(panel, addSelected=1)
    file_name = pm.playblast(f=os.path.join(ROOT, "data", name), fp=0, fmt="image", c="jpg", st=0, et=0, orn=1, os=True, qlt=100, p=100, wh=(128, 128), v=0)
    if os.path.isfile(file_name.replace("####", "0")):
        if os.path.isfile(file_name.replace("####.", "")):
            os.remove(file_name.replace("####.", ""))
        os.rename(file_name.replace("####", "0"), file_name.replace("####.", ""))
    if pm.modelPanel(panel, ex=1):
        pm.deleteUI(panel, panel=True)
    pm.delete(temp_curve)
    return name


def upload_select_curve():
    curve = get_selected_curve()
    if not curve:
        return
    return upload_curve(curve)


def load_curve(name):
    path = os.path.join(ROOT, "data", name+".json")
    if not os.path.isfile(path):
        return
    with open(path, "r") as read:
        points = json.loads(read.read())
    return pm.curve(d=1, n=name, p=points)


def load_curves(name):
    curves = pm.selected(type="transform")
    curve = load_curve(name)
    set_curve_radius(curve.getShape(), pm.softSelect(q=1, ssd=1))
    if not curves:
        return
    curve_shape = curve.getShape()
    replace_curves(curve_shape, curves)
    pm.delete(curve)
    pm.select(curves)


def delete_curve(name):
    path = os.path.join(ROOT, "data", name+".json")
    if os.path.isfile(path):
        os.remove(path)
    path = os.path.join(ROOT, "data", name+".jpg")
    if os.path.isfile(path):
        os.remove(path)


def replace_curves(origin_shape, curves):
    origin_color = origin_shape.attr("overrideColor").get()
    for curve in curves:
        old_shape = curve.getShape()
        if old_shape and old_shape.type() == "nurbsCurve":
            color = old_shape.overrideColor.get()
        else:
            color = origin_color
        pm.delete(curve.getShapes())
        copy_shape = origin_shape.copy(origin_shape, curve)
        copy_shape.rename(curve.name()+"Shape")
        copy_shape.overrideEnabled.set(1)
        copy_shape.overrideColor.set(color)


def replace_select_curves():
    curves = pm.selected(type="transform")
    if len(curves) < 2:
        return pm.warning("you should select curves")
    curve = curves.pop(-1)
    if not curve.getShape():
        return pm.warning("you should select curves")
    origin_shape = curve.getShape()
    if origin_shape.type() != "nurbsCurve":
        return pm.warning("you should select curves")
    replace_curves(origin_shape, curves)


def set_curve_color(curves, color):
    for curve in curves:
        curve_shape = curve.getShape()
        curve_shape.overrideEnabled.set(1)
        curve_shape.overrideColor.set(color)


def set_selected_curve_color(color):
    set_curve_color(get_selected_curves(), color)


def mirror_curve():
    curves = get_selected_curves()
    if len(curves) != 2:
        pass
    origin, mirror = curves
    points = pm.xform(origin.getShape().cv, q=1, t=1, ws=1)
    points = [points[i: i+3] for i in range(0, len(points), 3)]
    for point in points:
        point[0] = -point[0]
    curve_shape = mirror.getShape()
    for i, point in enumerate(points):
        pm.xform(curve_shape.cv[i], t=point, ws=1)
