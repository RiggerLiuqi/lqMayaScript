# coding:utf-8
import pymel.core as pm
import solver


def assert_geometry(geometry=None, shape_type="mesh"):
    if geometry is None:
        selected = pm.selected(o=1)
        if len(selected) != 1:
            return pm.warning("please select a " + shape_type)
        geometry = selected[0]
    if geometry.type() == shape_type:
        return geometry.getParent()
    if geometry.type() != "transform":
        return pm.warning("please select a " + shape_type)
    shape = geometry.getShape()
    if not shape:
        return pm.warning("please select a " + shape_type)
    if shape.type() != shape_type:
        return pm.warning("please select a " + shape_type)
    return geometry


def copy_weights():
    selected = pm.selected(o=1)
    if len(selected) < 2:
        return pm.warning(u"please select two object")
    if len(selected) > 2:
        src = selected[0]
        for dst in selected[1:]:
            pm.select(src, dst)
            copy_weights()
        return
    src, dst = selected
    if src.type() == "transform" and not src.getShape():
        name_polygon = {children.name().split("|")[-1]: children for children in src.getChildren(type="transform")}
        for children in dst.getChildren(type="transform"):
            name = children.split("|")[-1]
            if name in name_polygon:
                pm.select(name_polygon[name], children)
                copy_weights()
        return
    src, dst = assert_geometry(src, "mesh"), assert_geometry(dst, "mesh")
    if not all([src, dst]):
        return pm.warning(u"please select two polygon")
    skin_clusters = src.history(type="skinCluster")
    if len(skin_clusters) == 0:
        return pm.warning(u"please select two skin polygon")
    if dst.history(type="skinCluster"):
        return pm.mel.CopySkinWeights()
    pm.skinCluster(skin_clusters[0].getInfluence(), dst, tsb=1)
    pm.select(src, dst)
    pm.mel.CopySkinWeights()


def get_skin_cluster():
    polygon = assert_geometry(shape_type="mesh")
    if polygon is None:
        return
    for history in polygon.history(type="skinCluster"):
        return history
    pm.warning("\ncan not find skinCluster")


PAINT_WIDGETS = None


def copy_paint_widgets():
    skin_cluster = get_skin_cluster()
    if skin_cluster is None:
        return
    global PAINT_WIDGETS
    PAINT_WIDGETS = skin_cluster.paintWeights.get()
    pm.mel.mprint("\ncopy paint widgets successful")


def paste_paint_widgets():
    global PAINT_WIDGETS
    if PAINT_WIDGETS is None:
        pm.mel.warning("\ncan not find widgets")
    skin_cluster = get_skin_cluster()
    skin_cluster.paintWeights.set(PAINT_WIDGETS)
    pm.mel.mprint("\npaste paint widgets successful")


def get_length(p1, p2):
    return sum([(xyz1-xyz2)**2 for xyz1, xyz2 in zip(p1, p2)]) ** 0.5


def poly_to_edge():
    edge = pm.PyNode(pm.polyToCurve(form=2, degree=1, ch=0)[0])
    if edge.getShape().form() != 3:
        return
    curve_shape = edge.getShape()
    points = pm.xform(curve_shape.cv, q=1, ws=1, t=1)
    points = [points[i: i + 3] for i in range(0, len(points), 3)]
    xs = [p[0] for p in points]
    index = xs.index(min(xs))
    points = points[index:] + points[:index]
    for i, point in enumerate(points):
        pm.xform(curve_shape.cv[i], ws=1, t=point)
    xs = [p[0] for p in points]
    index = xs.index(max(xs))
    half_length = sum([get_length(points[i], points[i + 1]) for i in range(index)])
    number = 1
    n = (number + 1) * 2
    lengths = [half_length / n * i for i in range(n)]
    lengths += [half_length + (curve_shape.length() - half_length) / n * i for i in range(n)]
    skin_points = []
    for i, length in enumerate(lengths):
        param = curve_shape.findParamFromLength(length)
        point = curve_shape.getPointAtParam(param, space="world")
        skin_points.append(point)
    curves = []
    for i, point in enumerate(skin_points):
        curve = pm.curve(d=1, p=[[0, 0.1, 0], [0, -0.1, 0]], n="lipSecondary%02dCUR" % i)
        curve.setTranslation(point, space="world")
        curves.append(curve)
    surface = pm.loft(curves, ch=0, d=3, ss=1, c=1, u=1)[0]
    pm.duplicateCurve(surface.getShape().v[0.5], ch=0, rn=0, local=0)
    pm.delete(edge, surface, curves)


def surface_axis():
    surface = assert_geometry(shape_type="nurbsSurface")
    if surface is None:
        return
    follicle = pm.createNode("transform", n="SurfaceAxesFOL")
    pm.createNode("follicle", n="SurfaceAxesFOLShape", p=follicle)
    follicle.parameterU.set(0.5)
    follicle.parameterV.set(0.5)
    surface.local.connect(follicle.inputSurface)
    surface.worldMatrix.connect(follicle.inputWorldMatrix)
    follicle.outRotate.connect(follicle.rotate)
    follicle.outTranslate.connect(follicle.translate)
    pm.toggle(follicle, la=True)
    pm.select(surface)


def orient_joint_by_spine(joints, curve, start, end):
    for joint in joints[1:]:
        joint.setParent(w=1)
    for i, joint in enumerate(joints[:-1]):
        pm.delete(pm.aimConstraint(joints[i+1], joint))
    for i, joint in enumerate(joints[1:]):
        joint.setParent(joints[i])
    ik_hand, eef = pm.ikHandle(sj=joints[0], ee=joints[-1], c=curve, sol="ikSplineSolver", ccv=False)
    ik_hand.dTwistControlEnable.set(1)
    ik_hand.dWorldUpType.set(4)
    start.worldMatrix[0].connect(ik_hand.dWorldUpMatrix, f=1)
    end.worldMatrix[0].connect(ik_hand.dWorldUpMatrixEnd, f=1)
    tx = sum([rig_joint.tx.get() for rig_joint in joints[1:]])/len(joints[1:])
    for joint in joints[1:]:
        joint.tx.set(tx)
    pm.makeIdentity(joints, apply=True, r=True)
    joints[-1].rotate.set(0, 0, 0)
    joints[-1].jointOrient.set(0, 0, 0)
    pm.delete(ik_hand, eef)


def create_joints_by_curve(prefix, curve, number):
    curve_shape = curve.getShape()
    step = curve_shape.length() / (number - 1)
    pm.select(cl=1)
    joints = []
    for i in range(number):
        param = curve.getShape().findParamFromLength(step * i)
        joint = pm.joint(n=prefix+"%02dJNT" % (i+1))
        joints.append(joint)
        point = curve_shape.getPointAtParam(param, "world")
        joint.setTranslation(point, space="world")
    pm.makeIdentity(joints, apply=True, r=True)
    pm.joint(joints[0], e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
    joints[-1].rotate.set(0, 0, 0)
    joints[-1].jointOrient.set(0, 0, 0)
    return joints


def create_curve_by_joints(joints):
    points = [pm.xform(joint, q=1, ws=1, t=1) for joint in joints]
    curves = []
    for i, point in enumerate(points):
        curve = pm.curve(d=1, p=[[0, 0.1, 0], [0, -0.1, 0]], n="lipSecondary%02dCUR" % i)
        curve.setTranslation(point, space="world")
        curves.append(curve)
    surface = pm.loft(curves, ch=0, d=3, ss=1, u=1)[0]
    curve = pm.PyNode(pm.duplicateCurve(surface.getShape().v[0.5], ch=0, rn=0, local=0)[0])
    pm.delete(surface, curves)
    return curve


def rebuild_joint():
    selected = pm.selected(type="joint")
    if len(selected) == 1:
        joints = selected + list(reversed(selected[0].listRelatives(ad=1, type="joint")))
    else:
        curve = assert_geometry(shape_type="nurbsCurve")
        if curve is None:
            return
        joints = create_joints_by_curve("temp", curve, len(curve.getShape().ep))
    curve = create_curve_by_joints(joints)
    start = pm.group(em=1)
    start.setMatrix(joints[0].getMatrix(ws=1), ws=1)
    orient_joint_by_spine(joints, curve, start, start)
    pm.delete(curve, start)
    for joint in joints:
        if not pm.toggle(joint, q=1, la=1):
            pm.toggle(joint, la=True)
    pm.select(joints[0])


def make_curve_low(joints, radius):
    temp_curve = create_curve_by_joints(joints)
    temp_circle = pm.circle(ch=0, o=1, nr=[1, 0, 0])[0]
    temp_circle.setMatrix(joints[0].getMatrix(ws=1), ws=1)
    temp_circle.s.set(radius, radius, radius)
    temp_surface = pm.extrude(temp_circle, temp_curve, ch=0)[0]
    pm.delete(temp_curve, temp_circle)
    polygon = pm.PyNode(pm.nurbsToPoly(temp_surface, f=2, chr=0.01, pt=1, ut=3, vt=3, un=3, vn=4, ch=0)[0])
    pm.delete(temp_surface)
    pm.skinCluster(joints, polygon, tsb=1)
    pm.select(polygon)
    solver.paint_spine([[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]], radius=radius*1.4)


def make_select_curve_low():
    radius = pm.softSelect(q=1, ssd=1)
    selected = pm.selected(type="joint")
    if len(selected) == 1:
        joints = selected + list(reversed(selected[0].listRelatives(ad=1, type="joint")))
    else:
        return pm.warning("\n please select joint")
    make_curve_low(joints, radius)
