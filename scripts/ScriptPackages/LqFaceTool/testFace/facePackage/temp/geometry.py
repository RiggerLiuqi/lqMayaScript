# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    geometry
# .@Author:      CousinRig67
# .@Date:        2020-03-01
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

u"""
记录选择的模型名称到 |FaceGroup
"""


import pymel.core as pm
import json
from common import create_hierarchy_node


def selection_polygons():
    u"""
    获取选择的多边形
    :return:
    """

    polygons = []
    for sel in pm.selected(objectsOnly = True):     # objectsOnly只返回对象名称，而忽略组件/属性
        if sel.type() == 'mesh':
            polygons.append(sel.getParent())
        elif sel.type() == 'transform':
            if not sel.getShape():
                continue
            if sel.getShape().type() == 'mesh':
                polygons.append(sel)
    return polygons



def record_geometry(attribute = "face"):
    u"""
    记录选择的模型名称到 |FaceGroup 的 attribute

    :param name: 属性
    :return:
    """
    polygons = selection_polygons()

    info = json.dumps([polygon.fullPath() for polygon in polygons])

    face_group = create_hierarchy_node("|FaceGroup")
    # add attr

    if face_group.hasAttr(attribute):
        face_group.attr(attribute).set(info)
    else:
        face_group.addAttr(attribute, dataType = 'string')
        face_group.attr(attribute).set(info)

def read_geometry(attribute = 'face'):
    face_group = create_hierarchy_node('|FaceGroup')
    if not face_group.hasAttr(attribute):
        return []
    info = face_group.attr(attribute).get()
    # print 'Inf', info
    full_paths = json.loads(info)
    # print 'FullP', full_paths
    assert isinstance(full_paths, list)
    return [pm.PyNode(full_path) for full_path in full_paths if pm.objExists(full_path)]
