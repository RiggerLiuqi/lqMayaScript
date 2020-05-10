# coding:utf-8

import pymel.core as pm

import control
import actions



def brow_second_con(n, p, sx, radius, joint_group, SelectionBrowRoll, **kwargs):
    control_group = actions.create_group("|FaceGroup|FaceControlGroup|BrowControlGroup", init=False)
    roll_group = actions.create_group("|FaceGroup|FaceConnectGroup|BrowConnectGroup", init=False)

    second, con = actions.create_second_control(n=n, p=control_group)
    second.setTranslation(p, space="world")
    pm.delete(pm.aimConstraint(SelectionBrowRoll, second, wut="scene", aim=[0, 0, -1], wu=[0, 1, 0], u=[0, 1, 0]))
    control.control_create(con, s="ball", c=17, r=radius, o=[0, 0, radius * 2],
                           l=["sx", "sy", "sz", "v"])
    offset = pm.group(em=1, n=n+"Offset", p=roll_group)
    offset.setMatrix(con.getMatrix(ws=1), ws=1)
    offset.setTranslation(SelectionBrowRoll.getTranslation(space="world"), space="world")
    aim = pm.group(em=1, n=n+"Aim", p=offset)
    aim.setTranslation(con.getTranslation(space="world"), space="world")

    roll = pm.group(em=1, n=n+"Roll", p=offset)
    pm.aimConstraint(aim, roll, aim=[0, 0, 1], wut="none")

    parent = pm.group(em=1, n=n + "Parent", p=roll)
    parent.setTranslation(con.getTranslation(space="world"), space="world")
    con.r.connect(parent.r)

    offset.sx.set(sx)
    second.sx.set(sx)

    joint = pm.joint(joint_group, n=n + "Joint")
    joint.setMatrix(parent.getMatrix(ws=1), ws=1)
    pm.parent(pm.parentConstraint(parent, joint, mo=1), parent)
    joint.radius.set(radius)

    # jnt.t.connect(second.t)
    # jnt.r.connect(second.r)
    return aim, con, parent


def create_brow_second_cons(radius, joint_group, SelectionBrowCurve, SelectionBrowRoll, SelectionBrowJoint, **kwargs):
    points = actions.get_points_by_curve(curve=SelectionBrowCurve, number=5)
    results = [brow_second_con(p=[sx*t[0], t[1], t[2]], n="Brow{rl}{i:0>2}".format(rl=rl, i=i+1), **locals())
               for rl, sx in zip(["Rt", "Lf"], [1, -1]) for i, t in enumerate(points)]
    sx = 1
    results.append(brow_second_con(p=SelectionBrowJoint.getTranslation(space="world"), n="BrowMd", **locals()))
    return results


def set_brow_sdk(results, radius, **kwargs):
    control_group = actions.create_group("|FaceGroup|FaceControlGroup|BrowControlGroup", init=False)
    width = (results[4][0].getTranslation(space="world")[0] - results[0][0].getTranslation(space="world")[0])/2
    weights = [
         [1.0, 0.85, 0.5, 0.15, 0.0],
         [0.05, 0.35, 0.5, 0.35, 0.0],
         [0.0, 0.15, 0.5, 0.85, 1.0],
    ]
    for rl_field, rl_offset, rl_v in zip(["Rt", "Lf"], [1, -1], [0, 1]):
        group = pm.group(em=1, p=control_group, n="Brow{rl}ControlGroup".format(rl=rl_field))
        group.setMatrix(results[2+5*rl_v][0].getMatrix(ws=1), ws=1)
        main_con = control.control_create(
            p=group, l=["rx", "ry", "rz", "sx", "sy", "sz", "v"], s="browMain", c=13, r=radius*6,
            o=[0, 0, radius*4], n="Brow{rl}MainControl".format(rl=rl_field))
        arc_con = control.control_create(
            p=main_con, l=["rx", "ry", "rz", "sx", "sy", "sz", "v"], s="browArc", c=14, r=radius*4,
            o=[0, 0, radius*4], n="Brow{rl}ArcControl".format(rl=rl_field))

        for attr in ["TyOt", "TyMd", "TyIn", "TxOt", "TxIn"]:
            arc_con.addAttr(attr, max=1, min=0, at="double", k=1)
        for attr, dv_v in (["TyOt", [(-1, 1), (1, 0)]], ["TyMd", [(-1, 0), (0, 1), (1, 0)]], ["TyIn", [(-1, 0), (1, 1)]],
                           ["TxOt", [(1, 0), (9, 8*width)]], ["TxIn", [(-1, 0), (-9, -8*width)]]):
            for dv, v in dv_v:
                pm.setDrivenKeyframe(arc_con.attr(attr), cd=arc_con.tx, dv=dv*width, v=v)
        for i, (aim, con, parent), wts in zip(range(5), results[rl_v*5: rl_v*5+5], zip(*weights)):
            arc = pm.createNode("blendWeighted", n="Brow{rl}{i:0>2}ArcBlendWeighted".format(rl=rl_field, i=i+1))
            com_y = pm.createNode("blendWeighted", n="Brow{rl}{i:0>2}TyBlendWeighted".format(rl=rl_field, i=i + 1))
            com_z = pm.createNode("blendWeighted", n="Brow{rl}{i:0>2}TzBlendWeighted".format(rl=rl_field, i=i + 1))
            for j, (weight, attr) in enumerate(zip(wts, ["TyOt", "TyMd", "TyIn"])):
                con.addAttr(attr, at="double", k=0, dv=weight)
                pm.setAttr(con.attr(attr), cb=1)
                con.attr(attr).connect(arc.weight[j])
                arc_con.attr(attr).inputs(p=1)[0].connect(arc.input[j])
            con.addAttr("MainTy", at="double", k=0, dv=1)
            pm.setAttr(con.MainTy, cb=1)
            arc_con.ty.connect(com_y.input[0])
            main_con.ty.connect(com_y.input[1])
            con.ty.connect(com_y.input[2])
            arc.output.connect(com_y.weight[0])
            con.MainTy.connect(com_y.weight[1])
            com_y.weight[2].set(1)
            com_y.output.connect(aim.ty)

            arc_con.tz.connect(com_z.input[0])
            main_con.tz.connect(com_z.input[1])
            con.tz.connect(com_z.input[2])
            com_z.input[3].set(parent.tz.get())
            arc.output.connect(com_z.weight[0])
            con.MainTy.connect(com_z.weight[1])
            com_z.weight[2].set(1)
            com_z.weight[3].set(1)
            com_z.output.connect(parent.tz, f=1)

        tx_weights = [0.2, 0.5, 0.9, 0.95, 1.0], [1.0, 0.95, 0.9, 0.5, 0.2]

        for i, (aim, con, parent), ws in zip(range(5), results[rl_v * 5: rl_v * 5 + 5], zip(*tx_weights)):
            blend = pm.createNode("blendWeighted", n="Brow{rl}{i:0>2}TxBlendWeighted".format(rl=rl_field, i=i + 1))
            for j, attr in enumerate(["TxOt", "TxIn"]):
                con.addAttr(attr, at="double", k=0, dv=ws[j])
                pm.setAttr(con.attr(attr), cb=1)
                con.attr(attr).connect(blend.weight[j])
                arc_con.attr(attr).inputs(p=1)[0].connect(blend.input[j])
            main_con.tx.connect(blend.input[2])
            con.tx.connect(blend.input[3])
            blend.weight[2].set(1)
            blend.weight[3].set(1)
            blend.output.connect(aim.tx)

        for attr in ["TyOt", "TyMd", "TyIn", "TxOt", "TxIn"]:
            pm.deleteAttr(arc_con.attr(attr))

    ty_blend = pm.createNode("blendWeighted", n="BrowMdTyBlendWeighted")
    results[4][0].ty.connect(ty_blend.input[0])
    results[9][0].ty.connect(ty_blend.input[1])
    results[10][1].ty.connect(ty_blend.input[2])
    ty_blend.weight[0].set(0.5)
    ty_blend.weight[1].set(0.5)
    ty_blend.weight[2].set(1)
    ty_blend.output.connect(results[10][0].ty)

    tx_blend = pm.createNode("blendWeighted", n="BrowMdTxBlendWeighted")
    results[4][0].tx.connect(tx_blend.input[0])
    results[9][0].tx.connect(tx_blend.input[1])
    results[10][1].tx.connect(tx_blend.input[2])
    tx_blend.weight[0].set(0.2)
    tx_blend.weight[1].set(-0.2)
    tx_blend.weight[2].set(1)
    tx_blend.output.connect(results[10][0].tx)

    tz_blend = pm.createNode("blendWeighted", n="BrowMdTzBlendWeighted")
    results[4][2].tz.connect(tz_blend.input[0])
    results[9][2].tz.connect(tz_blend.input[1])
    results[10][1].tz.connect(tz_blend.input[2])
    tz_blend.weight[0].set(0.5)
    tz_blend.weight[1].set(0.5)
    tz_blend.weight[2].set(1)
    tz_blend.output.connect(results[10][2].tz)
    return


def brow_nose_rig():
    SelectionBrowNoseJoint, err = actions.find_node_by_name("SelectionBrowNoseJoint", False)
    BrowMdJoint, err = actions.find_node_by_name("BrowMdJoint", err)
    NoseUpJoint, err = actions.find_node_by_name("NoseUpJoint", err)
    if err:
        return
    joint_group = actions.create_joint("|FaceGroup|FaceJoint", init=False)
    connect_group = actions.create_group("|FaceGroup|FaceConnectGroup", init=False)
    control_group = actions.create_group("|FaceGroup|FaceControlGroup", init=False)

    n = "BrowNose"
    radius = BrowMdJoint.radius.get()
    offset = pm.group(em=1, p=connect_group, n=n + "Offset")
    offset.setMatrix(SelectionBrowNoseJoint.getMatrix(ws=1), ws=1)
    volume = pm.group(em=1, p=connect_group, n=n+"Volume")
    parent = pm.group(em=1, p=volume, n=n + "Parent")
    joint = pm.joint(joint_group, radius=radius, n=n + "Joint")
    second, con = actions.create_second_control(p=control_group, n=n, t=True, r=False)
    control.control_create(con, n=n + "Control", s="ball", c=17, r=radius, l=["sz", "sy", "sx", "v"])
    second.setMatrix(offset.getMatrix(ws=1), ws=1)
    con.t.connect(parent.t)
    con.r.connect(parent.r)
    joint.setMatrix(offset.getMatrix(ws=1), ws=1)
    pm.parent(pm.parentConstraint(parent, joint, mo=1), parent)
    pm.transformLimits(volume, tz=(0, 0), etz=(1, 0))

    blend = pm.createNode("blendWeighted", n=n+"BlendWeighted")

    blend.input[0].set(-NoseUpJoint.ty.get())
    NoseUpJoint.ty.connect(blend.input[1])
    con.addAttr("noseVolume", max=0, min=1, at="double", k=1, dv=0.2)
    con.noseVolume.connect(blend.weight[0])
    con.noseVolume.connect(blend.weight[1])

    blend.input[2].set(-BrowMdJoint.ty.get())
    BrowMdJoint.ty.connect(blend.input[3])
    con.addAttr("browVolume", max=0, min=1, at="double", k=1, dv=0.4)

    pm.setDrivenKeyframe(blend.weight[2], cd=con.browVolume, dv=0, v=0, itt="linear", ott="linear")
    pm.setDrivenKeyframe(blend.weight[2], cd=con.browVolume, dv=1, v=-1, itt="linear", ott="linear")
    blend.weight[2].inputs(p=1)[0].connect(blend.weight[3])

    blend.output.connect(volume.tz)


def brow_rig():
    err = False
    SelectionBrowCurve, err = actions.find_node_by_name("SelectionBrowCurve", err)
    SelectionBrowRoll, err = actions.find_node_by_name("SelectionBrowRoll", err)
    SelectionBrowJoint, err = actions.find_node_by_name("SelectionBrowJoint", err)
    if err:
        return
    if err:
        return pm.warning("can not din brow object")
    joint_group = actions.create_joint("|FaceGroup|FaceJoint|BrowJointGroup", init=True)
    connect_group = actions.create_group("|FaceGroup|FaceConnectGroup|BrowConnectGroup", init=True)
    control_group = actions.create_group("|FaceGroup|FaceControlGroup|BrowControlGroup", init=True)
    radius = SelectionBrowCurve.getShape().length()/4/10
    results = create_brow_second_cons(**locals())
    set_brow_sdk(**locals())
    brow_nose_rig()