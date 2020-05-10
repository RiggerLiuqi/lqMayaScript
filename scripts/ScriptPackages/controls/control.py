# coding=utf-8

"""
这是一个控制器类。用来上传、创建、修改控制器。
"""


import pymel.core as pm
import os
import json


class Control(object):
    u"""
    :param kwargs: 修改控制器的参数
    :param kwargs: -n -name string 名字
    :param kwargs: -t -transform string/node/Control 控制器
    :param kwargs: -p -parent string/node 父对象
    :param kwargs: -s -shape data/name 形态
    :param kwargs: -c -color int 颜色
    :param kwargs: -r -radius float 半径
    :param kwargs: -ro -rotate [float, float,float] 旋转
    :param kwargs: -o -offset [float, float,float] 偏移
    :param kwargs: -l -locked [str, ...] 偏移
    """
    @staticmethod
    def get_arg(args):
        if len(args) > 0:
            return args[0]
        return None

    @staticmethod
    def get_curve_shape_points(shape):
        return pm.xform(shape.cv, q=1, t=1)

    @staticmethod
    def get_soft_radius():
        return pm.softSelect(q=1, ssd=1)

    @staticmethod
    def get_length(point1, point2):
        return sum([(point1[i] - point2[i]) ** 2 for i in range(3)]) ** 0.5

    @classmethod
    def delete_shape(cls, *args, **kwargs):
        u"""
        删除形态
        """
        s = kwargs.get("s", kwargs.get("shape", cls.get_arg(args)))
        if s is None:
            return
        path = os.path.abspath(__file__+"/../data/{s}.json".format(s=s))
        if os.path.isfile(path):
            os.remove(path)
        path = os.path.abspath(__file__ + "/../data/{s}.jpg".format(s=s))
        if os.path.isfile(path):
            os.remove(path)

    @classmethod
    def delete_shapes(cls, *args, **kwargs):
        for s in args:
            cls.delete_shape(s)

    @classmethod
    def selected(cls):
        u"""
        :return: [Control(), ]
        选择的控制器
        """
        return [cls(t=t) for t in pm.selected(type="transform")]

    @classmethod
    def mirror_selected(cls):
        u"""
        镜像两个选择的控制器
        """
        selected = cls.selected()
        if not len(selected) == 2:
            return
        src, dst = selected
        src.mirror(dst)

    @classmethod
    def set_selected(cls, **kwargs):
        u"""
        :param kwargs: 修改控制器的参数
        批量修改选择的控制器
        """
        selected = cls.selected()
        for control in selected:
            control.set(**kwargs)
        pm.select([control.get_transform() for control in selected])

    def __init__(self, *args, **kwargs):
        self.transform = None
        self.set_transform(*args, **kwargs)
        self.set(**kwargs)

    def __str__(self):
        return self.get_transform().name()

    def __add__(self, other):
        return self.get_transform().name() + str(other)

    def __getattr__(self, item):
        if hasattr(Control, item):
            return Control.__getattribute__(self, item)
        else:
            return getattr(self.get_transform(), item)

    def set(self, **kwargs):
        u"""
        :param kwargs: 修改控制器的参数
        """
        self.set_parent(**kwargs)
        self.set_shape(**kwargs)
        self.set_name(**kwargs)
        self.set_color(**kwargs)
        self.set_radius(**kwargs)
        self.set_rotate(**kwargs)
        self.set_offset(**kwargs)
        self.set_locked(**kwargs)

    def set_transform(self, *args, **kwargs):
        u"""
        设置控制器
        """
        t = kwargs.get("t", kwargs.get("transform", self.get_arg(args)))
        if t is None:
            self.transform = pm.group(em=1)
        elif isinstance(t, (str, unicode)):
            if not pm.objExists(t):
                pm.warning("can not find " + t)
                self.set_transform()
            else:
                transforms = pm.ls(t, type="transform")
                if len(transforms) != 1:
                    pm.warning("the same name " + t)
                    self.transform = transforms[0]
                else:
                    self.transform = transforms[0]
        elif isinstance(t, Control):
            self.transform = t.transform
        elif hasattr(t, "nodeType") and t.nodeType() == "transform":
            self.transform = t

    def set_parent(self, *args, **kwargs):
        u"""
        设置父对像
        """
        p = kwargs.get("p", kwargs.get("parent", self.get_arg(args)))
        if p:
            self.get_transform().setParent(p)
            try:

                self.get_transform().t.set(0, 0, 0)
                self.get_transform().r.set(0, 0, 0)
                self.get_transform().s.set(1, 1, 1)
            except (RuntimeError, UnicodeEncodeError):
                pass

    def set_shape(self, *args, **kwargs):
        u"""
        设置形态
        """

        s = kwargs.get("s", kwargs.get("shape", self.get_arg(args)))
        c = self.get_color()
        r = self.get_radius()
        o = self.get_outputs()
        inputs = self.get_inputs()
        if s is None:
            return
        if isinstance(s, list):
            shapes = self.get_transform().getShapes()
            if shapes:
                pm.delete(shapes)
            for data in s:
                p = [[data["points"][i+j] for j in range(3)] for i in range(0, len(data["points"]), 3)]
                if data["periodic"]:
                    p = p + p[:data["degree"]]
                curve = pm.curve(degree=data["degree"],
                                 knot=data["knot"],
                                 periodic=data["periodic"],
                                 p=p)
                curve.getShape().setParent(self.get_transform(), s=1, add=1)
                curve.getShape().rename(self.get_transform().name().split("|")[-1]+"Shape")
                pm.delete(curve)
            self.set_color(c)
            self.set_radius(r)
            self.set_outputs(o)
            self.set_inputs(inputs)
        elif isinstance(s, (str, unicode)):
            data_file = os.path.abspath(__file__ + "/../data/{s}.json".format(s=s))
            if not os.path.isfile(data_file):
                pm.warning("can not find " + data_file)
                return
            with open(data_file, "r") as fp:
                self.set_shape(s=json.load(fp))

    def set_name(self, *args, **kwargs):
        u"""
        设置名字
        """
        n = kwargs.get("n", kwargs.get("name", self.get_arg(args)))
        if n is None:
            return
        self.get_transform().rename(n)
        for s in self.get_transform().getShapes():
            s.rename(n+"Shape")

    def set_color(self, *args, **kwargs):
        u"""
        设置颜色
        """
        c = kwargs.get("c", kwargs.get("color", self.get_arg(args)))
        if c is None:
            return
        for shape in self.get_transform().getShapes():
            if shape.nodeType() != "nurbsCurve":
                continue
            shape.overrideEnabled.set(True)
            shape.overrideColor.set(c)

    def set_radius(self, *args, **kwargs):
        u"""
        设置半径
        """
        r = kwargs.get("r", kwargs.get("radius", self.get_arg(args)))
        if r is None:
            return
        points = [self.get_curve_shape_points(shape) for shape in self.get_transform().getShapes()]
        points = [[[ps[i + j] for j in range(3)] for i in range(0, len(ps), 3)] for ps in points]
        lengths = [self.get_length(p, [0, 0, 0]) for ps in points for p in ps]
        origin_radius = max(lengths)
        scale = r/origin_radius
        for shape, ps in zip(self.get_transform().getShapes(), points):
            for p, cv in zip(ps, shape.cv):
                pm.xform(cv, t=[xyz*scale for xyz in p])

    def set_offset(self, *args, **kwargs):
        u"""
        设置偏移
        """
        o = kwargs.get("o", kwargs.get("offset", self.get_arg(args)))
        if o is None:
            return
        points = [self.get_curve_shape_points(shape) for shape in self.get_transform().getShapes()]
        points = [[[ps[i + j] for j in range(3)] for i in range(0, len(ps), 3)] for ps in points]
        for shape, ps in zip(self.get_transform().getShapes(), points):
            for p, cv in zip(ps, shape.cv):
                pm.xform(cv, t=[p_xyz+o_xyz  for p_xyz,o_xyz  in zip(p, o)])

    def set_rotate(self, *args, **kwargs):
        u"""
        设置旋转
        """
        o = kwargs.get("ro", kwargs.get("rotate", self.get_arg(args)))
        if o is None:
            return

        rotate = pm.datatypes.EulerRotation(o, unit="degrees")
        matrix = rotate.asMatrix()
        points = [self.get_curve_shape_points(shape) for shape in self.get_transform().getShapes()]
        points = [[[ps[i + j] for j in range(3)] for i in range(0, len(ps), 3)] for ps in points]
        for shape, ps in zip(self.get_transform().getShapes(), points):
            for p, cv in zip(ps, shape.cv):
                pm.xform(cv, t=pm.datatypes.Point(p) * matrix)

    def set_locked(self, *args, **kwargs):
        u"""
        设置属性锁定
        """
        l = kwargs.get("l", kwargs.get("locked", self.get_arg(args)))
        if l is None:
            return
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
            self.get_transform().attr(attr).setKeyable(True)
            self.get_transform().attr(attr).setLocked(False)
        for attr in l:
            if attr in "trs":
                for xyz in "xyz":
                    self.get_transform().attr(attr+xyz).setKeyable(False)
                    self.get_transform().attr(attr+xyz).setLocked(True)
            else:
                self.get_transform().attr(attr).setKeyable(False)
                self.get_transform().attr(attr).setLocked(True)

    def get_transform(self):
        u"""
        :return: transform node控制器节点

        """
        return self.transform

    def get_shape(self):
        u"""
        :return: data 控制器数据
        """
        return [dict(points=self.get_curve_shape_points(shape),
                     degree=shape.degree(),
                     periodic=shape.form() == 3,
                     knot=shape.getKnots())
                for shape in self.get_transform().getShapes()]

    def get_radius(self):
        u"""
        :return: radius float 控制器半径
        """
        if len(self.get_transform().getShapes()) == 0:
            return self.get_soft_radius()
        points = [self.get_curve_shape_points(shape) for shape in self.get_transform().getShapes()]
        points = [[[ps[i + j] for j in range(3)] for i in range(0, len(ps), 3)] for ps in points]
        lengths = [self.get_length(p, [0, 0, 0]) for ps in points for p in ps]
        radius = max(lengths)
        return radius

    def get_color(self):
        u"""
        :return: color int 控制器颜色
        """
        c = 0
        for shape in self.get_transform().getShapes():
            c = shape.overrideColor.get()
        return c

    def get_outputs(self):
        for shape in self.get_transform().getShapes():
            return [(out_attr.attrName(longName=True), in_attr)
                    for out_attr, in_attr in shape.outputs(p=1, connections=1)]
        return []

    def set_outputs(self, outputs):
        for shape in self.get_transform().getShapes():
            for out_attr, in_attr in outputs:
                if not shape.hasAttr(out_attr):
                    continue
                shape.attr(out_attr).connect(in_attr)

    def get_inputs(self):
        for shape in self.get_transform().getShapes():
            return [(in_attr.attrName(longName=True), out_attr)
                    for in_attr, out_attr in shape.inputs(p=1, connections=1)]
        return []

    def set_inputs(self, inputs):
        for shape in self.get_transform().getShapes():
            for in_attr, out_attr in inputs:
                if not shape.hasAttr(in_attr):
                    continue
                print in_attr, out_attr
                out_attr.connect(shape.attr(in_attr), f=1)

    def upload(self):
        u"""
        上传控制器
        """
        data_path = os.path.abspath(__file__+"/../data")
        if not os.path.isdir(data_path):
            pm.warning("can not find " + data_path)
            return
        data_file = os.path.join(data_path, self.get_transform().name().split("|")[-1]+".json")
        with open(data_file, "w") as fp:
            json.dump(self.get_shape(), fp, indent=4)
        for hud in pm.headsUpDisplay(lh=1):
            pm.headsUpDisplay(hud, e=1, vis=False)
        panel = "control_model_panel"
        if not pm.modelPanel(panel, ex=1):
            pm.modelPanel(panel, tearOff=True, toc=1)
        pm.modelEditor(panel, e=1, alo=0, nc=1, gr=False)
        pm.setFocus(panel)

        temp = Control()
        temp.set_shape(s=self.get_shape())
        pm.select(temp.get_transform())
        pm.setAttr("persp.r", -27.938, 45, 0)
        pm.viewFit("persp", an=0)
        pm.isolateSelect(panel, state=1)
        pm.isolateSelect(panel, addSelected=1)
        jpg_path = os.path.join(data_path, self.get_transform().name().split("|")[-1])
        file_name = pm.playblast(fmt="image", f=jpg_path, c="jpg", wh=[128, 128], st=0, et=0,
                                 viewer=False, percent=100, quality=100, fp=1)
        if os.path.isfile(file_name.replace("####", "0")):
            if os.path.isfile(file_name.replace("####.", "")):
                os.remove(file_name.replace("####.", ""))
            os.rename(file_name.replace("####", "0"), file_name.replace("####.", ""))
        if pm.modelPanel(panel, ex=1):
            pm.deleteUI(panel, panel=True)
        pm.delete(temp.get_transform())

    def mirror(self, other):
        u"""
        :param other: Control 镜像目标
        镜像控制器。
        """
        self.set_shape(s=other.get_shape())
        for src_shape, dst_shape in zip(self.get_transform().getShapes(), other.get_transform().getShapes()):
            for src_cv, dst_cv in zip(src_shape.cv, dst_shape.cv):
                point = pm.xform(dst_cv, q=1, t=1, ws=1)
                point[0] = -point[0]
                pm.xform(src_cv, t=point, ws=1)
