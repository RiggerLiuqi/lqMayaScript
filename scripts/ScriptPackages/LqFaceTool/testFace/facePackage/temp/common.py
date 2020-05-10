# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    common
# .@Author:      CousinRig67
# .@Date:        2020-03-02
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import maya.cmds as cmds
import pymel.core as pm
import json

u"""
通用函数模块
"""

def create_hierarchy_node(full_path = "|FaceGroup|LayerGroup", typ = 'transform'):
    u"""
    根据长名创建组层级

    :param full_path: 节点长名
    :return: node 创建的节点
    """

    if pm.objExists(full_path):
        return pm.PyNode(full_path)
    fields = full_path.split('|')
    name = fields.pop(-1)
    parent = '|'.join(fields)
    if len(fields) == 1:
        return pm.createNode(typ, n = name)
    else:
        return pm.createNode(typ, n = name, p = create_hierarchy_node(parent, typ))

def init_node(full_path):
    u"""
    删除存在的节点
    :param full_path: 节点长名
    :return:
    """

    if pm.objExists(full_path):
        pm.delete(full_path)