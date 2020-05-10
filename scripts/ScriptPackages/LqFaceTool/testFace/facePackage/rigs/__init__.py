# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    __init__.py
# .@Author:      CousinRig67
# .@Date:        2020-03-09
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#


# temp
# import sys
# print sys.path
# LqFacePath = r'F:\lqMayaScript\scripts\ScriptPackages\LqFaceTool\face\temp'
# if LqFacePath not in sys.path:
#     sys.path.append(LqFacePath)
#
# from common import create_hierarchy_node

from ..temp import common
reload(common)



class Rig(object):
    name = ''

    def __init__(self, fits):
        # 通用绑定内容
        self.fits = fits
        self.group = common.create_hierarchy_node('|FaceGroup|RigGroup|{group}Group'.format(group=fits.group))
        self.joint = common.create_hierarchy_node('|FaceGroup|FaceJoint|{layer}Joint'.format(layer = fits.layer), typ='joint')
        self.joint.drawStyle.set(2)

    def rig(self):
        # 基础绑定

        pass

    def sdk(self):
        # 联动

        pass
