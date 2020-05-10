# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    build
# .@Author:      CousinRig67
# .@Date:        2020-03-07
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

u"""
绑定函数入口
"""


# # temp
import sys
print sys.path
LqFacePath = r'F:\lqMayaScript\scripts\ScriptPackages\LqFaceTool\testFace'
if LqFacePath not in sys.path:
    sys.path.append(LqFacePath)
print sys.path


from facePackage.temp import fit
import pymel.core as pm
from facePackage.temp.common import create_hierarchy_node
from facePackage import rigs
reload(rigs)
from facePackage.rigs import point

reload(point)
print 'build import ok'

def RigBuild():
    # 隐藏定位器
    create_hierarchy_node('|FaceGroup|FitGroup').v.set(0)
    # 删除'FaceGroup' 下，除了 'FitGroup' 之外的组
    pm.delete([group for group in pm.listRelatives('|FaceGroup|') if group.name() != 'FitGroup'])
    create_hierarchy_node('|FaceGroup|FaceJoint', typ='joint').drawStyle.set(2)
    # 基础绑定
    for group, fits in fit.Fits()['group'].items():
        if fits.rig == 'point':
            rig = point.PointRig(fits)

        rig.rig()
