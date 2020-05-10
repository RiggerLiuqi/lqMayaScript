import pymel.core as pm

import actions
reload(actions)


def hide_control_joint():
    for joint in pm.ls("*ctrl"):
        if joint.type() == "joint":
            joint.drawStyle.set(2)


def edit_control(con):
    name = con.name()
    offset = actions.create_group("|PerseusGroup|{n}_offset".format(n=name), init=True)
    offset.inheritsTransform.set(0)
    offset.setMatrix(con.getMatrix(ws=1), ws=1)
    offset.v.set(0)
    edit = pm.group(em=1, n=name+"_edit", p=con.getParent())
    con.setParent(con)
    connect = pm.group(em=1, p=offset, n=name+"_connect")
    connect.t.connect(edit.t, f=1)
    connect.r.connect(edit.r, f=1)
    connect.s.connect(edit.s, f=1)
    mul_matrix = pm.createNode("multMatrix", n=name+"_multMatrix")
    con.matrix.connect(mul_matrix.matrixIn[0])
    edit.matrix.connect(mul_matrix.matrixIn[1])
    decompose_matrix = pm.createNode("decomposeMatrix", n=name+"_decomposeMatrix")
    mul_matrix.matrixSum.connect(decompose_matrix.inputMatrix)
    for trs in ["Translate", "Rotate", "Scale"]:
        for attr in con.attr(trs.lower()).outputs(p=1):
            decompose_matrix.attr("output" + trs).connect(attr, f=1)
        for xyz in "XYZ":
            for attr in con.attr(trs.lower()+xyz).outputs(p=1):
                decompose_matrix.attr("output"+trs+xyz).connect(attr, f=1)
    return connect


def edit_jaw():
    err = False
    JawDnJoint, err = actions.find_node_by_name("JawDnJoint", err)
    F_jaw_smooth, err = actions.find_node_by_name("F_jaw_smooth", err)
    F_facialHead_jnt_jnt, err = actions.find_node_by_name("F_facialHead_jnt_jnt", err)
    F_facialJaw_loc, err = actions.find_node_by_name("F_facialJaw_loc", err)
    F_facialJaw_jnt_skin = actions.find_node_by_name("F_facialJaw_jnt_skin", err)
    F_face_setDrv_grp = actions.find_node_by_name("F_facialJaw_loc", err)
    if err:
        return
    # pm.parentConstraint(JawDnJoint, F_facialJaw_loc, mo=1)
    drv = pm.joint(F_face_setDrv_grp, n="F_upLip_jnt_3_setDrv")
    parent = pm.parentConstraint(F_facialHead_jnt_jnt, F_facialJaw_jnt_skin, drv)[0]
    w1, w2 = pm.parentConstraint(parent, q=1, wal=1)
    w1.set(0)
    w2.set(1)


    #
    # name = F_facialHead_jnt_jnt.name()
    # offset = actions.create_group("|PerseusGroup|{n}_offset".format(n=name), init=True)
    # offset.inheritsTransform.set(0)
    # offset.setMatrix(F_facialHead_jnt_jnt.getMatrix(ws=1), ws=1)
    # head_connect = pm.group(em=1, p=offset, n=name+"_connect")
    # for constraint in set(F_jaw_smooth.outputs(type="parentConstraint")):
    #     head_connect.t.connect(constraint.target[0].targetTranslate, f=1)
    #     head_connect.r.connect(constraint.target[0].targetRotate, f=1)
    #     head_connect.s.connect(constraint.target[0].targetScale, f=1)
    # pm.parentConstraint(JawUpJoint, head_connect, mo=1)
    #
    # pm.parentConstraint("F_upLip_jnt_3_bind_grp")
    # up_lip_connect = edit_control(F_upLip_ctrl)
    # pm.parentConstraint(JawUpJoint, up_lip_connect, mo=1)

