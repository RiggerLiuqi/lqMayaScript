# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    lq_RigUI
# .@Author:      CousinRig67
# .@Date:        2019-12-23
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import os
import sys
import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

menuList = ['Rigging', 'Animation', 'TD', 'Others']
currentFilePath = r'{}'.format(os.path.dirname(__file__))
scriptPackagePath = r'{}\{}'.format(currentFilePath,  'ScriptPackages')
envPaths = [r'{}\{}'.format(currentFilePath, myTool) for myTool in menuList]
envPaths.append(scriptPackagePath)

for path in envPaths:
    if path in sys.path:
        print 'The python Env Path Already there!'
    else:
        sys.path.append(path)

for path in envPaths:
    if path in os.environ['MAYA_SCRIPT_PATH']:
        print 'The python Env Path Already there!'
    else:
        os.environ['MAYA_SCRIPT_PATH'] = '{};{}'.format(path, os.environ['MAYA_SCRIPT_PATH'])

menuItemList = []
for item in menuList:
    path  = r'{}\{}'.format(currentFilePath, item)
    for parent, dirnames, filenames in os.walk(path):

        if filenames:
            itemList = []
            for f in filenames:
                itemList.append(f.split('.')[0])
            menuItemList.append([item, itemList])

commandItemList = []
for item in menuItemList:
    commandItem = list(set(item[1]))
    commandItemList.append([item[0], commandItem])

# listA = menuItemList
# menuItemList = []
# for i in listA:
#     if i not in menuItemList:
#         menuItemList.append(i)
# [['Rigging', ['HZrig_controller', 'Rig_test']], ['Animation', ['Ani_test']], ['TD', ['TD_test']]]
print commandItemList


def lqRIG_UI():
    if cmds.menu('lq_RIG_Menu', ex=True):
        cmds.deleteUI('lq_RIG_Menu')
    gMainWindow = mel.eval('$tmpVar=$gMainWindow')

    lqMainMenu = cmds.menu('lq_RIG_Menu', label='LqRigTools', tearOff = True, p=gMainWindow)

    for m in commandItemList:
        cmds.menuItem(divider=True, dividerLabel='{}_Tools'.format(m[0]), p=lqMainMenu)
        lqRigMainMenu = cmds.menuItem('{}_menuItem'.format(m[0]), label='{}'.format(m[0]), subMenu = True,
                                      tearOff = True, p=lqMainMenu)
        for commandI in m[1]:
            lqRigSubMenu_01 = cmds.menuItem('{}_menuItem'.format(commandI), label='{}'.format(commandI),
                                            tearOff=True,
                                            p=lqRigMainMenu,
                                            c = 'import {0};reload({0});{0}.main()'.format(commandI))
    return True

def delect_lqRIG_UI():
    if cmds.menu('lq_RIG_Menu', ex=True):
        cmds.deleteUI('lq_RIG_Menu')
    return True

