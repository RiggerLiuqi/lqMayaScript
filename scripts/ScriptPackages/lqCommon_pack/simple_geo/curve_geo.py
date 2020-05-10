# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    curve_geo
# .@Author:      CousinRig67
# .@Date:        2020-04-26
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.cmds as cmds
import pymel.core as pm

def build_simple_curve():
    '''

    :return:
    '''
    select_jnts = pm.ls(sl = True, typ = 'joint', orderedSelection = True)
    for jnt in select_jnts:
        print jnt
        # jnt_matrix = jnt

build_simple_curve()