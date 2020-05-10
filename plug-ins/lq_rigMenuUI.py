# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    lq_rigMenuUI
# .@Author:      CousinRig67
# .@Date:        2019-12-23
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.cmds as cmds
import pymel.core as pm
import lq_RigUI
reload(lq_RigUI)

def load_lqRIG_UI():
    installUI = lq_RigUI.lqRIG_UI()

def unLoad_lq_RIG_UI():
    unInstallUI = lq_RigUI.delect_lqRIG_UI()

def initializePlugin(mobject):
    load_lqRIG_UI()

def uninitializePlugin(mobject):
    unLoad_lq_RIG_UI()



