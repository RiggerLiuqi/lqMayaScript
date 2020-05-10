# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    LiuQiController
# .@Author:      CousinRig67
# .@Date:        2020-01-14
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#
import os.path
import json
import maya.cmds as cmds
import pymel.core as pm



# ConDataPath = os.path.abspath(__file__+ r'\..\ConData')

class LqControl(object):

    @classmethod
    def selected(cls):
        return [cls(t = t)for t in pm.selected(typ = 'transform')]

    @classmethod
    def set_selected(cls, **kwargs):

        selected = cls.selected()
        [con.setCon(**kwargs) for con in selected]
        pm.select([con.get_transform() for con in selected])

    # @classmethod
    # def set_selected_color(cls, **kwargs):
    #     u"""
    #
    #     :param kwargs: -c -color int 颜色
    #
    #     :return:
    #     """
    #     [con.set_color(**kwargs) for con in cls.selected()]


    def __repr__(self):
        return "{modName}.{className}(trs = '{t}')".format(modName =__name__,
                                                         className = self.__class__.__name__,
                                                         t = self.get_transform())
    
    def __init__(self, **kwargs):
        u"""
        -n -name string 名字
        -t -transform string 控制器
        -p -parent string\node 父对象
        -c -color int 颜色
        """

        self.transform = None
        self.set_transform(**kwargs)


    def setCon(self, **kwargs):

        self.set_parent(**kwargs)
        self.set_shape(**kwargs)
        self.set_name(**kwargs)
        self.set_color(**kwargs)


    def set_parent(self, **kwargs):
        p = kwargs.get('p', None)
        if p:
            self.get_transform().setParent(p)

    def set_name(self, **kwargs):
        n = kwargs.get('n', '')
        # print n
        if n != '':

            self.get_transform().rename(n)
            # print self.get_transform().getShapes()
            for shape in self.get_transform().getShapes():

                shape.rename(n + "Shape")

    def set_transform(self, **kwargs):
        u"""
        -t -transform string 控制器
        """

        # t = kwargs.get('t', kwargs.get('t', None))
        t = kwargs.get('t',  None)
        # t = self.t

        if t is None:
            selected = pm.selected(typ = 'transform')

            if not selected:
                self.transform = pm.group(em = 1)
            else:
                self.transform = selected[0]

        elif isinstance(t, (str, unicode)):
            if not pm.objExists(t):
                pm.warning('can not find ' + t)
                self.set_transform()

            else:
                transforms = pm.ls(t, typ='transform', os = True)
                if len(transforms) != 1:
                    pm.warning('the same name' + t)
                    self.transform = transforms[0]
                else:
                    self.transform = transforms[0]

        elif isinstance( t, LqControl):
            self.transform = t

        elif hasattr(t, 'nodeType') and t.nodeType() == 'transform':
            self.transform = t
        # print "ok"
    def get_transform(self):
        return self.transform

    def set_color(self, **kwargs):
        u"""

        :param kwargs: -c -color int 颜色

        :return:
        """
        c = kwargs.get('c', kwargs.get('color', 1))
        # print c
        for shape in self.get_transform().getShapes():
            if shape.nodeType() != 'nurbsCurve':
                continue
            shape.overrideEnabled.set(True)
            shape.overrideColor.set(c)

    def get_shape(self, **kwargs):
        return [dict(points = self.get_curve_shape_points(shape),
              degree = shape.degree(),
              periodic = shape.form() == 3,
              knot = shape.getKnots())
         for shape in self.get_transform().getShapes()]

    @staticmethod
    def get_curve_shape_points(shape):
        return pm.xform(shape.cv, q = 1, t = True)

    def set_shape(self, **kwargs):
        u"""

        :param kwargs: -s -shape data/name 控制器形体名字
        :return:
        """
        s = kwargs.get('s', kwargs.get('shape', None))
        if s is None:
            return
        elif isinstance(s, list):
            shapes = self.get_transform().getShapes()
            if shapes:
                pm.delete(shapes)

            for data in s:
                p = [[data['points'][i + j] for j in range(0,3)] for i in range(0, len(data['points']), 3)]
                # print 'per>>>',data['periodic']
                # print 'S____', s
                # print 'K___',kwargs
                if data['periodic']:
                    p = p + p[:data['degree']]
                curve = pm.curve(degree = data['degree'],
                                 knot = data['knot'],
                                 periodic = data['periodic'],
                                 point = p
                                 )

                curve.getShape().setParent(self.get_transform(), s = True, add= True)
                curve.getShape().rename(self.get_transform().name().split('|')[-1] + "Shape")
                pm.delete(curve)
        elif isinstance( s, (str, unicode)):
            ConDataFile = os.path.abspath(__file__ + r'\..\ConData\{s}.json'.format(s = s))
            if not os.path.isfile(ConDataFile):
                pm.warning('can not find' + ConDataFile)
                return
            else:
                with open(ConDataFile, 'r') as fp:
                    self.set_shape(s = json.load(fp))

    @staticmethod
    def get_soft_radius():
        """

        :return: -r -radius float 软选半径
        """
        return pm.softSelect(q = True, ssd = True)

    @staticmethod
    def get_length(point1, point2):
        u"""

        :param point1: [float, float, float] 点坐标
        :param point2: [float, float, float] 点坐标
        :return: distance float 两点的距离
        """
        two_point_length = sum([(point1[i] - point2[i]) ** 2 for i in range(3)]) ** 0.5
        return two_point_length

    def set_radius(self, **kwargs):
        u"""

        :param kwargs: -r -radius float 半径
        :return:
        """
        r = kwargs.get('r', kwargs.get('radius', None))
        print r
        if r is None:
            return
        points = [self.get_curve_shape_points(shape) for shape in self.get_transform().getShapes()]

        points = [[[ps[i + j] for j in range(0, 3)] for i in range(0, len(ps), 3)]  for ps in points]
        print points
        lengths = [self.get_length(p, [0, 0, 0])for ps in points for p in ps]
        print 'lengths', lengths
        origin_radius = max(lengths)
        print origin_radius
        scale = r/origin_radius
        myZip = zip(self.get_transform().getShapes(), points)
        # print myZip
        for shape, ps in zip(self.get_transform().getShapes(), points):
            for p, cv in zip(ps, shape.cv):
                pm.xform(cv, t = [xyz * scale for xyz in p])






    def up_load(self):
        ConDataPath = os.path.abspath(__file__ + r'\..\ConData')
        if not os.path.isdir(ConDataPath):
            pm.warning('can not find ' + ConDataPath)
            return

        ConDataFile = os.path.join(ConDataPath, self.get_transform().name().split('|')[-1] + '.json')

        with open( ConDataFile, 'w') as fp:
            json.dump(self.get_shape(), fp, indent=4)


    def mirror(self):
        pass
