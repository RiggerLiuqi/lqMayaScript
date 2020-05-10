from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from controls.control import Control
from maya import cmds


def fk_rig(prefix="aaa"):
    joints = cmds.ls(sl=1)
    fk = cmds.group(n="{prefix}Group".format( prefix=prefix), em=1)
    radius = Control.get_soft_radius()
    for i, joint in enumerate(joints):
        group = cmds.createNode("transform", n="{prefix}{i:0>2}Group".format(i=i+1, prefix=prefix), p=joint)
        cmds.parent(group, fk)
        fk = Control(p=group, s="LiuJiaoTi", n="{prefix}{i:0>2}Control".format(i=i+1, prefix=prefix), ro=[0, -90, 90],
                     r=radius, c=17)
        ik = Control(p=fk, s="SanJiaoTi", n="{prefix}{i:0>2}SdControl".format(i=i+1, prefix=prefix), ro=[0, 0, 90],
                     r=radius*0.5, c=13, o=[0, radius*1.5, 0])
        cmds.setAttr(fk+".t", 0, 0, 0)
        cmds.setAttr(fk+".r", 0, 0, 0)
        cmds.createNode("joint", p=ik.get_transform().name(), n="{prefix}{i:0>2}Joint".format(i=i+1, prefix=prefix))

fk_rig(prefix="Tail")