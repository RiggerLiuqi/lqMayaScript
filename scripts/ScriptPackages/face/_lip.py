import pymel.core as pm

import control
import actions
import weight
import math
reload(weight)
reload(actions)


def lip_joints(SelectionLipUpCurve, SelectionLipDnCurve, joint_group, radius, **kwargs):
    up_points = actions.get_points_by_curve(SelectionLipUpCurve, 5)
    dn_points = actions.get_points_by_curve(SelectionLipDnCurve, 5)
    mid_points = [(up+dn)/2 for up, dn in zip(up_points, dn_points)]
    temp_curve = actions.create_curve_by_points(mid_points, n="temp", p=None)
    mid_points = actions.get_points_by_curve(temp_curve, 9)
    pm.delete(temp_curve)
    temp_curve = actions.rebuild_curve(curve=SelectionLipUpCurve, number=5)
    up_points = actions.get_points_by_curve(temp_curve, 9)
    pm.delete(temp_curve)
    up_points = [pm.datatypes.Point(m[0], u[1], u[2]) for u, m in zip(up_points, mid_points)]
    temp_curve = actions.rebuild_curve(curve=SelectionLipDnCurve, number=5)
    dn_points = actions.get_points_by_curve(temp_curve, 9)
    pm.delete(temp_curve)
    dn_points = [pm.datatypes.Point(m[0], d[1], d[2]) for d, m in zip(dn_points, mid_points)]
    up_curve = actions.create_curve_by_points(up_points)
    dn_curve = actions.create_curve_by_points(dn_points)
    joints = []
    step = 1.0 / 8
    for ud, curve, o in zip(["Up", "Dn"], [up_curve, dn_curve], [1, -1]):
        for i in range(1, 8, 1):
            joint = pm.joint(joint_group, n="Lip{ud}{i:0>2}Joint".format(ud=ud, i=i))
            actions.curve_group(curve=curve, group=joint, parm=step * i)
            joints.append(joint)
            joint.radius.set(radius)
    for rl, parm in zip(["Rt01", "Lf01"], [0, 1]):
        joint = pm.joint(joint_group, n="Lip{rl}Joint".format(rl=rl))
        actions.curve_group(curve=up_curve, group=joint, parm=parm)
        joints.append(joint)
        joint.radius.set(radius)
    pm.delete(up_curve, dn_curve)
    return joints


def main_connect(joints, radius, control_group,  **kwargs):
    err = False

    JawParent, err = actions.find_node_by_name("JawParent", err)
    JawTwistParent, err = actions.find_node_by_name("JawTwistParent", err)
    JawUpTwistParent, err = actions.find_node_by_name("JawUpTwistParent", err)
    SelectionLipJoint, err = actions.find_node_by_name("SelectionLipJoint", err)
    SelectionLipEnd, err = actions.find_node_by_name("SelectionLipEnd", err)
    JawControl, err = actions.find_node_by_name("JawControl", err)
    if err:
        return pm.warning("can not find jaw object")
    connect_group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup", init=False)
    offset = pm.group(em=1, n="LipOffset", p=connect_group)
    offset.setTranslation(SelectionLipJoint.getTranslation(space="world"), space="world")
    offset.tx.set(0)
    pm.parentConstraint(JawTwistParent, offset, mo=1)
    roll = pm.group(em=1, p=offset, n="LipRoll")
    twist = pm.group(em=1, p=roll, n="LipTwist")
    second, con = actions.create_second_control(p=control_group, n="Lip", t=True, r=True)
    control.control_create(con, s="lip", r=radius * 3, o=[0, 0, radius * 8], c=14,
                           l=["ry", "rx", "sx", "sy", "sz", "v"])
    second.setTranslation(SelectionLipEnd.getTranslation(space="world"), space="world")
    second.tx.set(0)

    factor = math.pi * (SelectionLipEnd.getTranslation(space="world")
                        - SelectionLipJoint.getTranslation(space="world")).length()
    unit_ry = pm.createNode("unitConversion", n="LipRollRyUnit")
    unit_ry.conversionFactor.set(factor)
    con.tx.connect(unit_ry.input)
    unit_ry.output.connect(roll.ry)
    unit_rx = pm.createNode("unitConversion", n="LipRollRxUnit")
    unit_rx.conversionFactor.set(-factor)
    con.ty.connect(unit_rx.input)
    unit_rx.output.connect(roll.rx)
    con.rz.connect(twist.rz)
    con.tz.connect(twist.tz)
    constraint = pm.parentConstraint(twist, second, mo=1)
    connect_group.worldInverseMatrix[0].connect(constraint.constraintParentInverseMatrix, f=1)
    skins = []
    parents = [[JawUpTwistParent], [JawParent], [JawTwistParent, JawParent], [JawTwistParent, JawParent]]
    for f, i, p, o in zip(["Up", "Dn", "Lf", "Rt"], [3, 10, 14, 15], parents, [1, -1, 0, 0]):
        follow = pm.group(n="Lip{f}Follow".format(f=f), em=1, p=twist)
        constraint = pm.parentConstraint(p, follow)
        offset.worldInverseMatrix[0].connect(constraint.constraintParentInverseMatrix, f=1)
        if len(p) == 2:
            w1, w2 = pm.parentConstraint(constraint, q=1, wal=1)
            JawControl.addAttr("Lip{f}Follow".format(f=f), max=5, min=-5, at="double", k=1)
            attr = JawControl.attr("Lip{f}Follow".format(f=f))
            pm.setDrivenKeyframe(w1, cd=attr, dv=-5, v=0, itt="linear", ott="linear")
            pm.setDrivenKeyframe(w1, cd=attr, dv=5, v=1, itt="linear", ott="linear")
            pm.setDrivenKeyframe(w2, cd=attr, dv=-5, v=1, itt="linear", ott="linear")
            pm.setDrivenKeyframe(w2, cd=attr, dv=5, v=0, itt="linear", ott="linear")
        _offset = pm.group(em=1, p=follow, n="Lip{f}Offset".format(f=f))
        _offset.setMatrix(joints[i].getMatrix(ws=1), ws=1)
        skin = pm.joint(_offset, n="Lip{f}JawSkin".format(f=f))
        skin.radius.set(radius)
        skins.append(skin)
        second, con = actions.create_second_control("Lip{f}".format(f=f), control_group, t=1, r=1)
        second.setMatrix(skin.getMatrix(ws=1), ws=1)
        control.control_create(con, s="point", r=radius*2, o=[0, o*2*radius, radius * 4], c=13,
                               l=["rx", "ry", "rz", "sx", "sy", "sz", "v"])
        con.t.connect(skin.t)
        con.r.connect(skin.r)
        constraint = pm.parentConstraint(skin, second, mo=1)
        connect_group.worldInverseMatrix[0].connect(constraint.constraintParentInverseMatrix, f=1)
        skins.append(skin)
    return


# def create_lip_second_cons(up_curve, dn_curve, radius, **kwargs):
#     second_cons = []
#     control_group = actions.create_group("|FaceGroup|FaceControlGroup|LipControlGroup", init=False)
#     step = 1.0 / 8
#     for ud, curve, o in zip(["Up", "Dn"], [up_curve, dn_curve], [1, -1]):
#         for i in range(1, 8, 1):
#             second, con = actions.create_second_control("Lip{ud}{i:0>2}".format(ud=ud, i=i+1),  control_group)
#             actions.curve_group(curve=curve, group=second, parm=step*i)
#             control.control_create(con, s="ball", r=radius, o=[0, o*radius, radius*2], c=17)
#             second_cons.append(con)
#     for rl, parm in zip(["Rt01", "Lf01"], [0, 1]):
#         second, con = actions.create_second_control("Lip{rl}".format(rl=rl), control_group)
#         actions.curve_group(curve=up_curve, group=second, parm=parm)
#         control.control_create(con, s="ball", r=radius, o=[0, 0, radius*2], c=17,
#                                l=["sx", "sy", "sz", "v"])
#         second_cons.append(con)
#     return second_cons
#
#
# def create_four_cons(second_cons, radius, **kwargs):
#     four_cons = []
#     control_group = actions.create_group("|FaceGroup|FaceControlGroup|LipControlGroup", init=False)
#     for field, i, o, in zip(["Up", "Dn", "Lf", "Rt"], [3, 10, -2, -1], [1, -1, 0, 0]):
#         second, con = actions.create_second_control("Lip{field}".format(field=field), control_group)
#         second.setMatrix(second_cons[i].getMatrix(ws=1), ws=1)
#         control.control_create(con, s="point", r=radius*2, o=[0, o*2*radius, radius * 4], c=13,
#                                l=["rx", "ry", "rz", "sx", "sy", "sz", "v"])
#         four_cons.append(con)
#     return four_cons
#
#
# def lip_roll_connect(radius, **kwargs):
#     err = False
#     JawUpTwistParent, err = actions.find_node_by_name("JawUpTwistParent", err)
#     JawParent, err = actions.find_node_by_name("JawParent", err)
#     SelectionLipJoint, err = actions.find_node_by_name("SelectionLipJoint", err)
#     SelectionLipEnd, err = actions.find_node_by_name("SelectionLipEnd", err)
#     LipJawPlane, err = actions.find_node_by_name("LipJawPlane", err)
#     if err:
#         return
#     control_group = actions.create_group("|FaceGroup|FaceControlGroup|LipControlGroup", init=False)
#     follow_group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup|lipFollow", init=False)
#     constraint = pm.parentConstraint(JawParent, JawUpTwistParent, follow_group)
#     w1, w2 = pm.parentConstraint(constraint, q=1, wal=1)
#     w1.set(0.5)
#     w2.set(0.5)
#     pre = pm.group(em=1, n="LipPre", p=follow_group)
#     pre.setTranslation(SelectionLipJoint.getTranslation(space="world"), space="world")
#     pm.delete(pm.aimConstraint(SelectionLipEnd, pre, wut="scene", aim=[0, 0, 1], skip=("y", "z")))
#     roll = pm.group(em=1, p=pre, n="LipRoll")
#     hand = pm.group(em=1, p=roll, n="LipHand")
#     control_follow = pm.group(em=1, p=control_group, n="LipControlFollow")
#     follow_group.t.connect(control_follow.t)
#     follow_group.r.connect(control_follow.r)
#
#     offset = pm.group(em=1, p=control_follow, n="LipOffset")
#     offset.setTranslation(SelectionLipEnd.getTranslation(space="world"), space="world")
#     pm.delete(pm.aimConstraint(SelectionLipJoint, offset, wut="scene", aim=[0, 0, -1], skip=("y", "z")))
#     con = pm.group(em=1, p=offset, n="LipControl")
#     control.control_create(con, s="lip", r=radius * 3, o=[0, 0, radius * 8], c=14,
#                            l=["ry", "sx", "sy", "sz", "v"])
#     factor = math.pi * (SelectionLipEnd.getTranslation(space="world") - SelectionLipJoint.getTranslation(space="world")).length()
#     unit_ry = pm.createNode("unitConversion", n="LipRollRyUnit")
#     unit_ry.conversionFactor.set(factor)
#     con.tx.connect(unit_ry.input)
#     unit_ry.output.connect(roll.ry)
#     unit_rx = pm.createNode("unitConversion", n="LipRollRxUnit")
#     unit_rx.conversionFactor.set(-factor)
#     con.ty.connect(unit_rx.input)
#     unit_rx.output.connect(roll.rx)
#     con.rz.connect(hand.rz)
#     con.tz.connect(hand.tz)
#     pm.select(LipJawPlane)
#     cluster, _ = pm.cluster(n="LipCluster", wn=(hand, hand))
#     pre.worldInverseMatrix[0].connect(cluster.bindPreMatrix)
#
#
# def four_connect(four_cons, second_cons, radius, **kwargs):
#     err = False
#     LipJawPlane, err = actions.find_node_by_name("LipJawPlane", err)
#     if err:
#         return
#     plane_group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup|lipPlaneGroup", init=False)
#     ty_plane = actions.create_plane(n="LipTyPlane", p=plane_group, transforms=second_cons, radius=radius)
#     tx_plane = actions.create_plane(n="LipTxPlane", p=plane_group, transforms=second_cons, radius=radius)
#     tz_plane = actions.create_plane(n="LipTzPlane", p=plane_group, transforms=second_cons, radius=radius)
#     point_plane = actions.create_plane(n="LipPointPlane", p=plane_group, transforms=second_cons, radius=radius)
#     aim_plane = actions.create_plane(n="LipAimPlane", p=plane_group, transforms=second_cons, radius=radius)
#
#     LipJawPlane.outMesh.connect(ty_plane.inMesh)
#     LipJawPlane.outMesh.connect(tx_plane.inMesh)
#     LipJawPlane.outMesh.connect(tz_plane.inMesh)
#     LipJawPlane.outMesh.connect(point_plane.inMesh)
#     LipJawPlane.outMesh.connect(aim_plane.inMesh)
#     ty_joints = []
#     tx_joints = []
#     attaches = []
#     group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup|LipFourGroup", init=False)
#     for field, i, con in zip(["Up", "Dn", "Lf", "Rt"], [3, 10, 14, 15], four_cons):
#         attach = actions.create_attach(p=group, n="Lip{f}Attach".format(f=field), i=i, plane=LipJawPlane)
#         ty_joint = pm.joint(attach, n="Lip{f}TySkin".format(f=field))
#         tx_joint = pm.joint(attach, n="Lip{f}TxSkin".format(f=field))
#         tx_joint.v.set(0)
#         ty_joint.v.set(0)
#         tx_joint.radius.set(radius)
#         ty_joint.radius.set(radius)
#         ty_joints.append(ty_joint)
#         tx_joints.append(tx_joint)
#         con.ty.connect(ty_joint.ty)
#         con.tx.connect(tx_joint.tx)
#         con.tz.connect(tx_joint.tz)
#         attaches.append(attach)
#     ty_skin = pm.skinCluster(ty_joints, ty_plane, n="LipTySK")
#     tx_skin = pm.skinCluster(tx_joints, tx_plane, n="LipTxSK")
#     tz_skin = pm.skinCluster(tx_joints, tz_plane, n="LipRollSK")
#     weight.load_weight(ty_skin, "LipTyPlane")
#     weight.load_weight(tx_skin, "LipTxPlane")
#     weight.load_weight(tz_skin, "LipTyPlane")
#
#     # roll_skin = pm.skinCluster(tx_joints, roll_plane, n="LipRollSK")
#     for i in range(4):
#         attaches[i].worldInverseMatrix[0].connect(tx_skin.bindPreMatrix[i])
#         attaches[i].worldInverseMatrix[0].connect(ty_skin.bindPreMatrix[i])
#         attaches[i].worldInverseMatrix[0].connect(tz_skin.bindPreMatrix[i])
#     pm.blendShape(tx_plane, ty_plane, tz_plane,  point_plane, n="LipFourBS", w=((0, 1), (1, 1), (2, 1)))
#     pm.blendShape(tx_plane, ty_plane, aim_plane, n="LipFourBS", w=((0, 1), (1, 1)))
#     tx_joints[0].worldInverseMatrix[0].connect(tx_skin.bindPreMatrix[0], f=1)
#     tx_joints[1].worldInverseMatrix[0].connect(tx_skin.bindPreMatrix[1], f=1)
#     tx_joints[2].worldInverseMatrix[0].connect(tz_skin.bindPreMatrix[2], f=1)
#     tx_joints[3].worldInverseMatrix[0].connect(tz_skin.bindPreMatrix[3], f=1)


def second_connect(second_cons, radius, **kwargs):
    err = False
    SelectionNoseEnd, err = actions.find_node_by_name("SelectionNoseEnd", err)
    LipPointPlane, err = actions.find_node_by_name("LipPointPlane", err)
    LipAimPlane, err = actions.find_node_by_name("LipAimPlane", err)
    if err:
        return
    group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup|LipSecondGroup", init=False)
    joints = []
    height = SelectionNoseEnd.getTranslation(space="world")[1] - second_cons[3].getTranslation(space="world")[1]
    for i, con in enumerate(second_cons):
        point = actions.create_attach(p=group, n=con.name().replace("Control", "PointAttach"), plane=LipPointPlane, i=i)
        joint = pm.joint(point, n=con.name().replace("Control", "Skin"))
        con.t.connect(joint.t)
        joints.append(joint)
        joint.radius.set(radius)
        if "Up" in con.name():
            aim = actions.create_attach(p=group, n=con.name().replace("Control", "AimAttach"), plane=LipAimPlane, i=i)
            offset = pm.group(em=1, p=aim, n=con.name().replace("Control", "AimOffset"))
            constraint = pm.aimConstraint(offset, joint, aim=[0, 1, 0], wut="none")
            offset.ty.set(height)
            con.r.connect(constraint.offset)
        elif "Dn" in con.name():
            aim = actions.create_attach(p=group, n=con.name().replace("Control", "AimAttach"), plane=LipAimPlane, i=i)
            offset = pm.group(em=1, p=aim, n=con.name().replace("Control", "AimOffset"))
            constraint = pm.aimConstraint(offset, joint, aim=[0, 1, 0], wut="none")
            offset.ty.set(-height)
            con.r.connect(constraint.offset)
        else:
            con.r.connect(joint.r)
    points = [con.getTranslation(space="world") for con in second_cons]
    points = [points[14]] + points[:7] + [points[15]] + list(reversed(points[7:13]))
    # points.insert(8, points.pop(14))
    actions.create_surface_by_points(points=points, c=1, liner_point=[[0, radius*0.2, 0], [0, -radius*0.2, 0]])
    return joints


def second_cons():
    pass


def lip_rig(**kwargs):
    err = False
    SelectionLipUpCurve, err = actions.find_node_by_name("SelectionLipUpCurve", err)
    SelectionLipDnCurve, err = actions.find_node_by_name("SelectionLipDnCurve", err)
    if err:
        return pm.warning("can not find jaw object")
    joint_group = actions.create_joint("|FaceGroup|FaceJointGroup|LipJointGroup", init=True)
    connect_group = actions.create_group("|FaceGroup|FaceConnectGroup|LipConnectGroup", init=True)
    control_group = actions.create_group("|FaceGroup|FaceControlGroup|LipControlGroup", init=True)

    radius = SelectionLipDnCurve.getShape().length()/40

    joints = lip_joints(**locals())
    main_connect(**locals())
    second_connect(**locals())
