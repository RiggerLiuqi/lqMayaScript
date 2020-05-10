# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    fitMeng
# .@Author:      CousinRig67
# .@Date:        2020-03-05
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

# coding:utf-8
u"""
定位绑定位置，点，线，骨骼，轴心，循环边等。
"""
import pymel.core as pm
from common import create_hierarchy_node, init_node
# import yaml
# import os


class Fit(object):
    u"""
    node：定位器节点
    layout: 绑定函数生成的绑定骨骼蒙皮的模型层
    group: 定位器组，同组的定位器，作为参数，传入一个绑定函数。
    rig: 绑定函数
    field: 用来区分同组下相同fit类型的定位器
    fit: 定位器类型，point,center,curve等
    rml: 左中右 用来镜像或区分非对称模型
    other: 记录函数参数
    """
    def __init__(self, **kwargs):
        self.node = kwargs.get("node", None)
        self.layout = kwargs.get("layout", None)
        self.group = kwargs.get("group", None)
        self.field = kwargs.get("field", None)
        self.rml = kwargs.get("side", None)
        self.rig = kwargs.get("rig", None)
        self.fit = kwargs.get("fit", None)

    def __setattr__(self, key, value):
        if key == "node":
            return object.__setattr__(self, key, value)
        if isinstance(value, (str, unicode)):
            if self.node.hasAttr(key):
                self.node.attr(key).set(value)
            else:
                self.node.addAttr(key, dt="string")
                self.node.attr(key).set(value)
        if isinstance(value, int):
            if self.node.hasAttr(key):
                self.node.attr(key).set(value)
            else:
                self.node.addAttr(key, at="long", k=1)
                self.node.attr(key).set(value)

    def __getattribute__(self, item):
        if item == "node":
            return object.__getattribute__(self, "node")
        return self.node.attr(item).get()


class Fits(list):
    u"""
    方便对所有Fit进行分组，获取属性
    """
    def __init__(self, _list=None):
        if _list is None:
            list.__init__([])
            fit_group = create_hierarchy_node("|FaceGroup|FitGroup")
            for node in fit_group.listRelatives(ad=1):
                if node.hasAttr("fit"):
                    self.append(Fit(node=node))
        else:
            list.__init__(_list)

    def __getitem__(self, item):
        if isinstance(item, (str, unicode)):
            result = {}
            for _fit in self:
                result.setdefault(getattr(_fit, item), Fits([])).append(_fit)
            return result
        else:
            return list.__getitem__(self, item)

    def __getattribute__(self, item):
        if hasattr(list, item):
            return list.__getattribute__(self, item)
        else:
            return getattr(self[0], item)


def fit_point(name="Check"):
    u"""
    创建定位点, 选择模型上点运行
    :param name: 名称
    :return:
    """
    name = "Fit{name}Point".format(name=name)
    points = [sel.getPosition(space="world") for sel in pm.selected(fl=1) if isinstance(sel, pm.general.MeshVertex)]
    if len(points) == 0:
        return pm.warning("please select vertex")
    center = sum(points)/len(points)
    group = create_hierarchy_node("|FaceGroup|FitGroup|FitPointGroup")
    init_node("|FaceGroup|FitGroup|FitPointGroup|{name}".format(name=name))
    joint = pm.joint(group, n=name)
    joint.t.set(center)
    locator = pm.group(em=1, p=joint, n=name+"Locator")
    pm.createNode("locator", p=locator, n=name+"LocatorShape")
    joint.radius.connect(locator.sx)
    joint.radius.connect(locator.sy)
    joint.radius.connect(locator.sz)
    pm.toggle(joint, la=1)
    locator.overrideEnabled.set(True)
    locator.overrideDisplayType.set(1)
    pm.select(joint)
    Fit(node=joint, fit="Point")
    return [joint]


def polygon_to_curve(side_length):
    u"""
    :param side_length: 顶点线个数，循环边为0， 线段为2
    :return: 从多边形线上提取的曲线。
    """
    edges = [sel for sel in pm.selected(fl=1) if isinstance(sel, pm.general.MeshEdge)]
    if len(edges) < 2:
        return pm.warning("please select edge")
    sides = [edge for edge in edges if len(set(edges) & set(edge.connectedEdges())) == 1]
    if len(sides) != side_length:
        return pm.warning("please select edge")
    return pm.PyNode(pm.polyToCurve(degree=1, ch=0)[0])


def init_curve(ft, curve, name):
    u"""
    重构曲线为x轴从左到右，并放到|FaceGroup|FitGroup|FitCurveGroup|{name}
    :param ft: 定位器类型
    :param curve: 曲线
    :param name: 曲线名
    :return:
    """
    group = create_hierarchy_node("|FaceGroup|FitGroup|Fit{ft}Group".format(ft=ft))
    init_node("|FaceGroup|FitGroup|Fit{ft}Group|{name}".format(name=name, ft=ft))
    curve.setParent(group)
    curve.rename(name)
    p1 = curve.cv[0].getPosition(space="world")
    p2 = curve.cv[-1].getPosition(space="world")
    if p1[0] > p2[0]:
        pm.reverseCurve(curve)
    return curve


def fit_curve(name="Brow"):
    u"""
    创建定位线，选择模型上线运行
    :param name: 名称
    :return:
    """
    name = "Fit{name}Curve".format(name=name)
    curve = polygon_to_curve(2)
    init_curve("Curve", curve, name)
    pm.select(curve)
    Fit(node=curve, fit="Curve")
    return [curve]


def fit_loopCurve(name="Lip"):
    u"""
    创建定位循环边，选择模型上线运行
    :param name: 名称
    :return:
    """
    name = "Fit{name}Curve".format(name=name)
    ps = [sel.getPosition(space="world") for sel in pm.selected(fl=1) if isinstance(sel, pm.general.MeshVertex)]
    curve = polygon_to_curve(0)
    points = [cv.getPosition(space="world") for cv in curve.cv]
    pm.delete(curve)
    if len(ps) == 2:
        ds1 = [(ps[0]-p).length() for p in points]
        ds2 = [(ps[1]-p).length() for p in points]
        ids = sorted([ds1.index(min(ds1)), ds2.index(min(ds2))])
    else:
        xs = [p[0] for p in points]
        ids = sorted([xs.index(min(xs)), xs.index(max(xs))])
    up_points = points[ids[0]:ids[1]+1]
    dn_points = points[ids[1]:]+points[:ids[0]+1]
    if sum([p[1] for p in up_points])/len(up_points) < sum([p[1] for p in dn_points])/len(dn_points):
        up_points, dn_points = dn_points, up_points
    up_curve = pm.curve(p=up_points, d=1)
    dn_curve = pm.curve(p=dn_points, d=1)
    pm.select(up_curve, dn_curve)
    init_curve("Loop", up_curve, name+"Up")
    init_curve("Loop", dn_curve, name+"Dn")
    Fit(node=up_curve, fit="UpCurve")
    Fit(node=dn_curve, fit="DnCurve")
    return [up_curve, dn_curve]


def fit_center(name="Jaw"):
    u"""
    创建定位轴心, 选择模型上点运行
    :param name: 名称
    :return:
    """
    points = [sel.getPosition(space="world") for sel in pm.selected(fl=1) if isinstance(sel, pm.general.MeshVertex)]
    if len(points) == 0:
        return pm.warning("please select vertex")
    group = create_hierarchy_node("|FaceGroup|FitGroup|FitCenterGroup")
    init_node("|FaceGroup|FitGroup|FitCenterGroup|Fit{name}Aim".format(name=name))
    center = sum(points)/len(points)
    prefix = "Fit" + name
    aim = pm.joint(group, n=prefix+"Aim")
    aim.t.set(center)
    center = pm.joint(aim, n=prefix+"Center")
    center.t.set(0, 0, -1)

    sphere = pm.PyNode(pm.polySphere(n=prefix+"Sphere", ch=0)[0])
    sphere.setParent(center)
    sphere.t.set(0, 0, 0)
    sphere.overrideEnabled.set(1)
    sphere.overrideDisplayType.set(1)

    pm.aimConstraint(aim, center, aim=[0, 1, 0], u=[1, 0, 0], wu=[1, 0, 0], wuo=aim, wut="objectrotation")
    distance = pm.createNode("distanceBetween", n=prefix+"Distance")
    center.t.connect(distance.point1)
    distance.distance.connect(sphere.sx)
    distance.distance.connect(sphere.sy)
    distance.distance.connect(sphere.sz)
    pm.select(center)
    Fit(node=aim, fit="Aim")
    Fit(node=center, fit="Center")
    return [aim, center]


def fit_elliptic(name="Brow"):
    u"""
    创建定位双轴心, 选择模型上点运行
    :param name: 名称
    :return:
    """
    points = [sel.getPosition(space="world") for sel in pm.selected(fl=1) if isinstance(sel, pm.general.MeshVertex)]
    if len(points) == 0:
        return pm.warning("please select vertex")
    group = create_hierarchy_node("|FaceGroup|FitGroup|FitEllipticGroup")
    init_node("|FaceGroup|FitGroup|FitCenterGroup|Fit{name}Locator".format(name=name))
    center = sum(points)/len(points)
    prefix = "Fit" + name
    aim = pm.joint(em=1, p=group, n=prefix+"Aim")
    aim.t.set(center)
    center_x = pm.joint(aim, n=prefix + "CenterX")
    center_y = pm.group(center_x, n=prefix + "CenterY")
    center_x.tz.set(-3)
    center_y.tz.set(1)
    pm.aimConstraint(aim, center_x, aim=[0, 0, 1], u=[1, 0, 0], wu=[1, 0, 0], wuo=aim, wut="objectrotation")
    for attr in ["tx", "ty", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
        center_y.attr(attr).setLocked(True)
    distance = pm.createNode("distanceBetween", n=prefix+"Distance")
    center_x.t.connect(distance.point1)
    unit = pm.createNode("unitConversion", n=prefix+"Unit")
    unit.conversionFactor.set(-1)
    center_y.tz.connect(unit.input)
    curves = []
    for i in range(7):
        p = "{prefix}{i:0>2}".format(prefix=prefix, i=i+1)
        offset = pm.group(em=1, p=center_y, n=p+"Offset")
        offset.ry.set(-60+20*i)
        curve = pm.circle(nr=[1, 0, 0], ch=0, sw=120)[0]
        curve.v.set(0)
        curve.setParent(offset)
        curve.t.set(0, 0, 0)
        curve.r.set(30, 0, 0)
        unit.output.connect(curve.tz)
        distance.distance.connect(curve.sx)
        distance.distance.connect(curve.sy)
        distance.distance.connect(curve.sz)
        curves.append(curve)
    surface = pm.PyNode(pm.loft(curves, ss=2, ch=1)[0])
    surface.rename(prefix + "Surface")
    surface.setParent(aim)
    surface.inheritsTransform.set(0)
    surface.overrideEnabled.set(1)
    surface.overrideDisplayType.set(1)
    surface.t.set(0, 0, 0)
    pm.select(center_x)
    Fit(node=aim, fit="Aim")
    Fit(node=center_x, fit="CenterX")
    Fit(node=center_y, fit="CenterY")
    return [aim, center_x, center_y]


def fit_joint(name="Squash"):
    u"""
    创建定位骨骼, 选择自己创建的骨骼运行
    :param name:
    :return:
    """
    joints = pm.selected(type="joint")
    if len(joints) != 1:
        return pm.warning("please select joint")
    joint = joints[0]
    joints = [joint] + list(reversed(joint.listRelatives(ad=1)))
    group = create_hierarchy_node("|FaceGroup|FitGroup|FitJointGroup")
    full_path = "|FaceGroup|FitGroup|FitJointGroup|Fit{name}01Joint".format(name=name)
    if joints[0].fullPath() != full_path:
        init_node("|FaceGroup|FitGroup|FitJointGroup|Fit{name}01Joint".format(name=name))
    joints[0].setParent(group)
    for i, joint in enumerate(joints):
        joint.rename("Fit{name}{i:0>2}Joint".format(name=name, i=i+1))
    pm.select(joints[0])
    for i, joint in enumerate(joints):
        Fit(node=joint, fit="Joint{i:0>2}".format(i=i+1))
    return joints


def fit(**kwargs):
    # path = os.path.abspath("{_file}/../configs/fits/{project}/{name}.yam".format(_file=__file__, project=project, name=name))
    # if not os.path.isfile(path):
    #     pm.warning("can not file {project} {name}".format(project=project, name=name))
    # with open(path, "r") as ft:
    #     data = ft.read()
    #     kwargs = yaml.load(data)
    group = kwargs.setdefault("group", "base")
    field = kwargs.setdefault("field", "")
    rml = kwargs.setdefault("rml", "Middle")
    name = "{group}{field}{rml}".format(group=group, field=field, rml=rml)
    nodes = globals()["fit_"+kwargs.get("fit", "point")](name)
    for node in nodes:
        _fit = Fit(node=node)
        for attr, value in kwargs.items():
            if attr == "fit":
                continue
            setattr(_fit, attr, value)


