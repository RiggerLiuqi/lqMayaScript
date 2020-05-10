# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    HZrig_controller
# .@Author:      CousinRig67
# .@Date:        2019-12-24
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm


modulePath = cmds.getModulePath(moduleName='lq_rig_tools')

def main(*args):
    doP =  mel.eval(r'source "{}/scripts/ScriptPackages/HZrig_controller/HZrig_controllers_UI.mel";'.format(modulePath))
    print modulePath
