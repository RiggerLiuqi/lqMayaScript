# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    dpRig
# .@Author:      CousinRig67
# .@Date:        2020-05-11
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.cmds as cmds
import dpAutoRigSystem
import dpAutoRigSystem.dpAutoRig as dpAR
reload(dpAR)

def main():

    dpUI = dpAR.DP_AutoRig_UI()