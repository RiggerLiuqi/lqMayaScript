# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    test
# .@Author:      CousinRig67
# .@Date:        2020-01-14
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.cmds as cmds
import pymel.core as pm

import sys
sys.path.append(r'F:\lqMayaScript\scripts\ScriptPackages\LqController')
from LqControllerPackage import LiuQiController as lqc
reload(lqc)


def makeCon():
    con = lqc.LqControl()
    con.set_color(c = 13)
    con.set_name(n = 'L_arm_con')
    con.set_parent(p = 'null1')

def upload_all():
    for t in pm.ls(sl = True, typ = 'transform'):
        lqc.lqControl(t = t).up_load()

def set_colors():
    for t in pm.ls(sl = True, typ = 'transform'):
        lqc.LqControl(t = t, c = 12)

def set_controls():
    for t in pm.ls(sl = True, typ = 'transform'):
        lqc.LqControl(t = t, s = 'cube')

if __name__ == "__main__":
    # makeCon()
    con = lqc.LqControl()
    con.set_name(n = 'myCon')
    shapeData = con.get_shape()
    print shapeData




