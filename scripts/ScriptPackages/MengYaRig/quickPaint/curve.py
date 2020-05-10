# coding:utf-8

import pymel.core as pm
from ..controls import action
import tools
import solver
reload(tools)


def create_locator(prefix, group, curve):
    u"""
    :param prefix: 前缀
    :param group: 所在组
    :param curve: 曲线
    :return:
    """
    curve_shape = curve.getShape()
    locators = []
    for i, cv in enumerate(curve_shape.cv):
        loc = pm.spaceLocator()
        locators.append(loc)
        loc.v.set(0)
        point = pm.xform(cv, q=1, t=1, ws=1)
        pm.xform(loc,  t=point, ws=1)
        loc.setParent(group)
        loc.rename(prefix + "%02dLOC" % (i + 1))
        loc.worldPosition[0].connect(curve_shape.controlPoints[i])
    return locators


def create_ik_hand(prefix, group, joints, curve, control):
    """
    :param prefix: 前缀
    :param group: 所在组
    :param joints: 谷歌
    :param curve: 曲线
    :param control: 控制器
    :return:
    """
    ik_hand, eef = pm.ikHandle(sj=joints[0], ee=joints[-1], c=curve, sol="ikSplineSolver", ccv=False)
    ik_hand.setParent(group)
    ik_hand.rename(prefix+"IKH")
    ik_hand.v.set(False)
    eef.rename(prefix+"EFF")
    # ik hand
    curve.setParent(group)
    curve.inheritsTransform.set(0)
    curve.rename(prefix+"CUR")
    curve.v.set(False)
    curve.t.set(0, 0, 0)
    curve.r.set(0, 0, 0)
    # curve
    stretch_length = pm.arclen(curve, ch=1)
    stretch_length.rename(prefix + "StretchLengthCVI")
    base_length = pm.createNode("multiplyDivide", n=prefix+"BaseLengthMUL")
    base_length.input1X.set(stretch_length.arcLength.get())
    if not pm.pluginInfo("matrixNodes", q=1, l=1):
        pm.loadPlugin("matrixNodes")
    decompose = pm.createNode("decomposeMatrix", n=prefix+"lengthMUL")
    group.worldMatrix[0].connect(decompose.inputMatrix)
    decompose.outputScaleX.connect(base_length.input2X)
    length_scale = pm.createNode("multiplyDivide", n=prefix+"LengthScaleMUL")
    length_scale.operation.set(2)
    stretch_length.arcLength.connect(length_scale.input1X)
    base_length.outputX.connect(length_scale.input2X)
    stretch_switch = pm.createNode("multiplyDivide", n=prefix+"StretchSwitchMUL")
    stretch_switch.operation.set(3)
    control.addAttr("stretchy", at="double", min=0, dv=1, max=1, k=1)
    control.stretchy.connect(stretch_switch.input2X)
    length_scale.outputX.connect(stretch_switch.input1X)
    tx = pm.createNode("multiplyDivide", n=prefix + "TxMUL")
    tx.input1X.set(sum([rig_joint.tx.get() for rig_joint in joints[1:]])/len(joints[1:]))
    stretch_switch.outputX.connect(tx.input2X)
    for joint in joints[1:]:
        tx.outputX.connect(joint.tx)
    # stretch
    volume_switch = pm.createNode("multiplyDivide", n=prefix+"VolumeSwitchMUL")
    volume_switch.input1X.set(-0.5)
    control.addAttr("volume", at="double", min=0, dv=1, max=1, k=1)
    control.volume.connect(volume_switch.input2X)
    sy_sz = pm.createNode("multiplyDivide", n=prefix+"SySzMUL")
    stretch_switch.outputX.connect(sy_sz.input1X)
    volume_switch.outputX.connect(sy_sz.input2X)
    sy_sz.operation.set(3)
    for joint in joints:
        sy_sz.outputX.connect(joint.sy)
        sy_sz.outputX.connect(joint.sz)
    # volume
    return ik_hand


def make_deformation(prefix, group, ik_joints):
    deformation = pm.group(em=1)
    deformation.setParent(group)
    deformation.rename("DeformationSystem")
    constraint = pm.group(em=1)
    constraint.setParent(group)
    constraint.rename("ConstraintSystem")
    joints = []
    pm.select(deformation)
    for i, ik_joint in enumerate(ik_joints):
        joint = pm.joint()
        joints.append(joint)
        joint.setMatrix(ik_joint.getMatrix(ws=1), ws=1)
        joint.rename(prefix + "%02dJNT" % (i+1))
        ik_joint.rename(prefix + "%02dIK" % (i+1))
        pm.makeIdentity(joint, apply=True, r=True)
        pm.parent(pm.parentConstraint(ik_joint, joint, mo=1), constraint)
        ik_joint.s.connect(joint.s)
        pm.select(joint)
    ik_joints[0].v.set(0)
    return joints


def tail_rig(prefix="tall", number=3):
    u"""
    :param prefix: 前缀
    :param number: 分段数
    :return:
    """
    pm.select(hi=1)
    origins = pm.selected(type="joint")
    if len(origins) < 2:
        return pm.warning("you should select joint hierarchy top")
    radius = pm.softSelect(q=1, ssd=1)
    group = pm.group(em=1)
    group.rename(prefix+"NUL")
    group.setMatrix(origins[0].getMatrix(ws=1), ws=1)
    fk_cons = []
    for i, joint in enumerate(origins):
        fk_con = action.load_curve("cuboid")
        fk_cons.append(fk_con)
        action.set_curve_radius(fk_con.getShape(), radius * 1.5)
        fk_con.rename(prefix + "Fk%02dCON" % (i + 1))
        for attr in ["sx", "sy", "sz", "v"]:
            fk_con.attr(attr).setLocked(True)
            fk_con.attr(attr).setKeyable(False)
        con_grp = pm.group(em=1)
        fk_con.setParent(con_grp)
        con_grp.setParent(group)
        con_grp.rename(prefix+"%02dFkNUL" % (i+1))
        con_grp.setMatrix(joint.getMatrix(ws=1), ws=1)
    for i, fk_con in enumerate(fk_cons[1:]):
        fk_con.getParent().setParent(fk_cons[i])
    action.set_curve_color(fk_cons, 17)
    curve = tools.create_curve_by_joints(origins)
    locators = create_locator(prefix, group, curve)
    ik_cons = []
    for i, fk_con in enumerate(fk_cons):
        ik_con = action.load_curve("star")
        ik_cons.append(ik_con)
        action.set_curve_radius(ik_con.getShape(), radius * 1.2)
        for attr in ["rx", "ry", "rz", "sx", "sy", "sz", "v"]:
            ik_con.attr(attr).setLocked(True)
            ik_con.attr(attr).setKeyable(False)
        con_grp = pm.group(em=1)
        ik_con.setParent(con_grp)
        ik_con.rename(prefix + "Ik%02dCON" % (i + 1))
        con_grp.rename(prefix+"%02dIkNUL" % (i+1))
        con_grp.setParent(fk_con)
        con_grp.setMatrix(locators[i+1].getMatrix(ws=1), ws=1)
        locators[i + 1].setParent(ik_con)
        con_grp.r.set(0, 0, 0)
    locators[0].setParent(fk_cons[0])
    locators[-1].setParent(fk_cons[-1])
    action.set_curve_color(ik_cons, 22)
    ik_joints = tools.create_joints_by_curve(prefix, curve, number*(len(origins)-1)+1)
    tools.orient_joint_by_spine(ik_joints, curve, origins[0], origins[-1])
    ik_joints[0].setParent(fk_cons[0])
    ik_joints[0].rename(prefix+"01JNT")
    ik_hand = create_ik_hand(prefix, group, ik_joints, curve, fk_cons[-1])
    twist_plu = pm.createNode("plusMinusAverage", n=prefix+"TwistPLU")
    for i, fx_con in enumerate(fk_cons[1:]):
        fx_con.rx.connect(twist_plu.input1D[i])
    if origins[1].tx.get() > 0:
        twist_plu.output1D.connect(ik_hand.twist)
    else:
        twist_mul = pm.createNode("multiplyDivide", n=prefix + "TwistMUL")
        twist_plu.output1D.connect(twist_mul.input1X)
        twist_mul.input2X.set(-1)
        twist_mul.outputX.connect(ik_hand.twist)
    joints = make_deformation(prefix, group, ik_joints)
    tools.make_curve_low(joints, radius)


def ball_rig(prefix="ball", number=7):
    u"""
    :param prefix: 前缀
    :param number: 分段数
    :return:
    """
    pm.select(hi=1)
    origins = pm.selected(type="joint")
    if len(origins) != 2:
        return pm.warning(u"please select two joints")
    radius = origins[1].tx.get()/2
    group = pm.group(em=1)
    group.rename(prefix+"NUL")
    pm.delete(pm.orientConstraint(origins[0], group))
    pm.delete(pm.pointConstraint(origins, group))
    main_con = action.load_curve("cube")
    action.set_curve_radius(main_con.getShape(), radius * 1.8)
    main_con.setParent(group)
    main_con.setMatrix(group.getMatrix(ws=1), ws=1)
    main_con.rename(prefix+"CON")
    action.set_curve_color([main_con], 17)
    cons = []
    for i in range(3):
        con = action.load_curve("ball")
        cons.append(con)
        action.set_curve_radius(con.getShape(), radius * 0.2)
        con_group = pm.group(em=1)
        con.setParent(con)
        con.rename(prefix + "%02dCON" % i)
        con_group.setParent(main_con)
        con_group.rename(prefix + "%02dNUL" % i)
        con_group.setMatrix(group.getMatrix(ws=1), ws=1)
        for attr in ["ry", "rz", "sx", "sy", "sz", "v"]:
            con.attr(attr).setLocked(True)
            con.attr(attr).setKeyable(False)
    cons[1].rx.setLocked(True)
    cons[1].rx.setKeyable(False)
    action.set_curve_color(cons, 17)
    cons[0].getParent().setTranslation(origins[0].getTranslation(space="world"), space="world")
    cons[2].getParent().setTranslation(origins[1].getTranslation(space="world"), space="world")
    pm.select(cons[1])
    action.load_curves("cuboid")
    action.set_curve_radius(cons[1].getShape(), radius * 1.4)
    pm.pointConstraint(cons[0], cons[2], cons[1].getParent(), mo=1, skip=("y", "z"))
    points = [joint.getTranslation(space="world") for joint in origins]
    curve = pm.curve(d=2, ep=points)
    locators = create_locator(prefix, group, curve)
    for con, locator in zip(cons, locators):
        locator.setParent(con)
    ik_joints = tools.create_joints_by_curve(prefix, curve, number)
    ik_joints[0].setParent(cons[0])
    ik_joints[0].rename(prefix+"01JNT")
    tools.orient_joint_by_spine(ik_joints, curve, origins[0], origins[0])
    ik_hand = create_ik_hand(prefix, main_con, ik_joints, curve, cons[2])
    cons[2].volume.outputs()[0].input1X.set(-1)
    twist_mul = pm.createNode("multiplyDivide", n=prefix + "TwistMUL")
    twist_mul.input2X.set(-1)
    cons[0].rx.connect(twist_mul.input1X)
    twist_plu = pm.createNode("plusMinusAverage", n=prefix+"TwistPLU")
    twist_mul.outputX.connect(twist_plu.input1D[0])
    cons[2].rx.connect(twist_plu.input1D[1])
    twist_plu.output1D.connect(ik_hand.twist)
    polygon = pm.polySphere(ch=0, sx=32, sy=32)[0]
    polygon.rz.set(90)
    pm.select(polygon)
    pm.makeIdentity(apply=1, t=1, r=1, s=1)
    polygon.setParent(group)
    polygon.inheritsTransform.set(0)
    polygon.rename(prefix+"LowPOL")
    polygon.setMatrix(group.getMatrix(ws=1), ws=1)
    polygon.s.set(radius, radius, radius)
    pm.select(polygon)
    pm.makeIdentity(apply=1, t=1, r=1, s=1)
    polygon.setPivots([0, 0, 0])
    joints = make_deformation(prefix, main_con, ik_joints)
    pm.skinCluster(joints, polygon)
    pm.select(polygon)
    solver.paint_spine([[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]], radius=radius * 1.4)


