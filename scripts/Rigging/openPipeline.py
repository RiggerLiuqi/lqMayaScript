# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    openPipeline
# .@Author:      CousinRig67
# .@Date:        2019-12-30
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.mel as mel
import maya.cmds as cmds
modulePath = cmds.getModulePath(moduleName='lq_rig_tools')

def main():
    mel.eval(r'source "{}/scripts/ScriptPackages/openPipeline_0.9.2/openPipeline.mel";'.format(modulePath))
    mel.eval("openPipeline;")
