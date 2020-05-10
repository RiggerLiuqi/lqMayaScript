# coding:utf-8

import pymel.core as pm
from . import tools
from ..controls import action
reload(tools)
reload(action)


def make_follicle(geometry=None, name="follicle", u=0, v=0):
    u"""
    创建follicle.
    :param geometry: 几何体
    :param name: follicle节点名。
    :param u: follicle节点ParameterU的数值。
    :param v: follicle节点Parameter的数值
    :return: follicle节点。
    """
    if geometry is None:
        geometry = pm.selected()[0]
    follicle = pm.createNode("transform", n=name)
    pm.createNode("follicle", n=name+"Shape", p=follicle)
    follicle.parameterU.set(u)
    follicle.parameterV.set(v)
    follicle.inheritsTransform.set(False)
    if geometry.getShape().type() == "mesh":
        geometry.outMesh.connect(follicle.inputMesh)
    else:
        geometry.local.connect(follicle.inputSurface)
    geometry.worldMatrix.connect(follicle.inputWorldMatrix)
    follicle.outRotate.connect(follicle.rotate)
    follicle.outTranslate.connect(follicle.translate)
    follicle.getShape().v.set(0)
    return follicle


def get_uvs(surface, d=1):
    shape = surface.getShape()
    us = [1.0/shape.spansU.get()*i/d for i in range(shape.spansU.get()*d)]
    vs = [1.0/shape.spansV.get()*i/d for i in range(shape.spansV.get()*d)]
    if shape.formInU() != 3:
        us.append(1.0)
    if shape.formInV() != 3:
        vs.append(1.0)
    for i, u in enumerate(us):
        if u == 0.0:
            us[i] += 0.001
        if u == 0.5:
            us[i] += 0.001
        if u == 1.0:
            us[i] -= 0.001
    return us, vs


def cloth_rig(prefix="cloth", number=2):
    surface = tools.assert_geometry(shape_type="nurbsSurface")
    if surface is None:
        return
    surface = surface.duplicate()[0]
    group = pm.group(em=1, n=prefix+"NUL")
    surface.setParent(group)
    surface.rename(prefix)
    surface.inheritsTransform.set(0)
    surface.v.set(0)

    con_root = pm.group(em=1)
    con_root.setParent(group)
    con_root.rename(prefix+"ConNUL")

    fol_root = pm.group(em=1)
    fol_root.setParent(group)
    fol_root.rename(prefix+"FolNUL")

    us, vs = get_uvs(surface, d=1)
    fol_us, fol_vs = get_uvs(surface, d=number)
    shape = surface.getShape()
    radius = (shape.area()/shape.spansU.get()/shape.spansV.get())**0.5/4
    cons = []
    skins = []
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            temp = make_follicle(surface, prefix+"u%02dv%02dTemp" % (i+1, j+1), u, v)
            con_grp = pm.group(em=1)
            con = action.load_curve("cube")
            action.set_curve_radius(con.getShape(), radius)
            joint = pm.joint()
            joint.v.set(0)
            joint.setParent(con)
            joint.rename(prefix+"u%02dv%02dSK" % (i+1, j+1))
            con.setParent(con_grp)
            con.rename(prefix+"u%02dv%02dCON" % (i+1, j+1))
            con_grp.setParent(con_root)
            con_grp.rename(prefix+"u%02dv%02dNUL" % (i+1, j+1))
            con_grp.setMatrix(temp.getMatrix(ws=1), ws=1)
            cons.append(con)
            pm.delete(temp)
            skins.append(joint)
    action.set_curve_color(cons, 17)
    for u in range(len(us[1:])):
        for v in range(len(vs)):
            cons[(u + 1) * len(vs) + v].getParent().setParent(cons[u * len(vs) + v])
    # surface skin
    pm.rebuildSurface(surface, su=shape.spansU.get(), sv=shape.spansV.get()*2, ch=0)
    skin_cluster = pm.skinCluster(skins, surface, mi=1)
    weights = []
    wts = {-1: 0.5, 0: 1, 1: 0.5}
    for vtx_u in range(shape.numCVsInU()):
        for vtx_v in range(shape.numCVsInV()):
            for joint_u in range(len(us)):
                for joint_v in range(len(vs)):
                    wu = int(min(max(vtx_u - 1, 0), shape.numCVsInU() - 3) == joint_u)
                    if shape.formInV() == 3:
                        vtx_id = vtx_v - 1
                        if vtx_v == 0:
                            if joint_v == len(vs)-1 or joint_v == 0:
                                wv = 0.5
                            else:
                                wv = 0
                        else:
                            wv = wts.get(joint_v * 2 - vtx_id, 0)
                    else:
                        vtx_id = min(max(vtx_v - 1, 0), shape.numCVsInV() - 3)
                        wv = wts.get(joint_v*2-vtx_id, 0)
                    weights.append(wu*wv)
    skin_cluster.setWeights(shape, range(len(skins)), weights)

    deformation = pm.group(em=1)
    deformation.setParent(group)
    deformation.rename("DeformationSystem")

    constraint = pm.group(em=1)
    constraint.setParent(group)
    constraint.rename("ConstraintSystem")

    joints = []
    us, vs = fol_us, fol_vs
    if not pm.pluginInfo("matrixNodes", q=1, l=1):
        pm.loadPlugin("matrixNodes")
    decompose = pm.createNode("decomposeMatrix", n=prefix+"ScaleDEC")
    group.worldMatrix[0].connect(decompose.inputMatrix)
    for j, v in enumerate(vs):
        for i, u in enumerate(us):
            follicle = make_follicle(surface, prefix+"u%02dv%02dFol" % (i+1, j+1), u, v)
            pm.select(follicle)
            joint = pm.joint(n=prefix+"u%02dv%02dJNT" % (i+1, j+1))
            if i == 0:
                joint.setParent(deformation)
            else:
                joint.setParent(joints[-1])
            pm.parent(pm.parentConstraint(follicle, joint), constraint)
            joints.append(joint)
            follicle.setParent(fol_root)
            follicle.getShape().v.set(0)
            decompose.outputScale.connect(follicle.s)

    # polygon skin
    polygon = pm.PyNode(pm.nurbsToPoly(surface, f=2, chr=0.01, pt=1, ut=3, un=number*2, vt=3, vn=number, ch=0)[0])
    polygon.setParent(group)
    polygon.rename(prefix+"LowPOL")
    skin_cluster = pm.skinCluster(joints, polygon)
    spans_u = int(shape.spansU.get())
    spans_v = int(shape.spansV.get()/2)
    mesh = polygon.getShape()
    weights = []
    for v in mesh.vtx:
        vtx_u, vtx_v = int(round(min(v.getUVs()[0])*spans_u*2*number)), int(round(min(v.getUVs()[1])*spans_v*2*number))
        for joint_v in range(len(vs)):
            for joint_u in range(len(us)):
                length_u, length_v = abs(joint_u*2 - vtx_u), abs(joint_v*2 - vtx_v)
                if shape.formInU() == 3:
                    index_u = min(spans_u * 2 * number - length_u, length_u, 4)
                else:
                    index_u = min(length_u, 4)
                if shape.formInV() == 3:
                    index_v = min(spans_v * 2 * number - length_v, length_v, 4)
                else:
                    index_v = min(length_v, 4)
                if shape.formInU() != 3 and joint_u in [0, len(us)-1]:
                    default_u = [0.8, 0.5, 0.2, 0.05, 0]
                else:
                    default_u = [0.6, 0.45, 0.2, 0.05, 0]
                if shape.formInV() != 3 and joint_v in [0, len(vs)-1]:
                    default_v = [0.8, 0.5, 0.2, 0.05, 0]
                else:
                    default_v = [0.6, 0.45, 0.2, 0.05, 0]
                weights.append(default_u[index_u]*default_v[index_v])
    skin_cluster.setWeights(polygon.getShape(), range(len(joints)), weights)


def belt_rig(prefix="cloth", number=1):
    surface = tools.assert_geometry(shape_type="nurbsSurface")
    if surface is None:
        return
    surface = surface.duplicate()[0]
    group = pm.group(em=1, n=prefix + "NUL")
    surface.setParent(group)
    surface.rename(prefix)
    surface.inheritsTransform.set(0)
    surface.v.set(0)

    con_root = pm.group(em=1)
    con_root.setParent(group)
    con_root.rename(prefix + "ConNUL")

    fol_root = pm.group(em=1)
    fol_root.setParent(group)
    fol_root.rename(prefix+"FolNUL")

    us, vs = get_uvs(surface, d=1)
    shape = surface.getShape()
    radius = (shape.area()/shape.spansU.get()/shape.spansV.get())
    cons = []
    skins = []
    for i, u in enumerate(us):
        temp = make_follicle(surface, prefix + "%02dTemp" % (i+1), u, 0.5)
        con_grp = pm.group(em=1)
        con = action.load_curve("cube")
        action.set_curve_radius(con.getShape(), radius)
        joint = pm.joint()
        joint.v.set(0)
        joint.setParent(con)
        joint.rename(prefix + "%02dSK" % (i + 1))
        con.setParent(con_grp)
        con.rename(prefix + "%02dCON" % (i + 1))
        con_grp.setParent(con_root)
        con_grp.rename(prefix + "%02dNUL" % (i + 1))
        con_grp.setMatrix(temp.getMatrix(ws=1), ws=1)
        cons.append(con)
        pm.delete(temp)
        skins.append(joint)
    pm.skinCluster(skins, surface, mi=1)
    action.set_curve_color(cons, 17)

    deformation = pm.group(em=1)
    deformation.setParent(group)
    deformation.rename("DeformationSystem")

    constraint = pm.group(em=1)
    constraint.setParent(group)
    constraint.rename("ConstraintSystem")

    joints = []
    us, vs = get_uvs(surface, d=number)
    if not pm.pluginInfo("matrixNodes", q=1, l=1):
        pm.loadPlugin("matrixNodes")
    decompose = pm.createNode("decomposeMatrix", n=prefix+"ScaleDEC")
    group.worldMatrix[0].connect(decompose.inputMatrix)
    for i, u in enumerate(us):
        follicle = make_follicle(surface, prefix + "%02dFol" % (i + 1), u, 0.5)
        pm.select(follicle)
        joint = pm.joint(n=prefix + "%02dJNT" % (i + 1))
        follicle.setParent(fol_root)
        follicle.getShape().v.set(0)
        decompose.outputScale.connect(follicle.s)
        if i == 0:
            joint.setParent(deformation)
        else:
            joint.setParent(joints[-1])
        pm.makeIdentity(joint, apply=True, r=True)
        pm.parent(pm.parentConstraint(follicle, joint), constraint)
        joints.append(joint)
    polygon = pm.PyNode(pm.nurbsToPoly(surface, f=2, chr=0.01, pt=1, ut=3, un=number*2, vt=3, vn=1, ch=0)[0])
    polygon.inheritsTransform.set(0)
    skin_cluster = pm.skinCluster(joints, polygon)
    polygon.setParent(group)
    polygon.rename(prefix+"LowPOL")
    spans_u = int(shape.spansU.get())
    mesh = polygon.getShape()
    weights = []
    for v in mesh.vtx:
        vtx_u = int(round(min(v.getUVs()[0])*spans_u*2*number))
        for joint_u in range(len(us)):
            length_u = abs(joint_u*2 - vtx_u)
            if shape.formInU() == 3:
                index_u = min(spans_u * 2*number - length_u, length_u, 4)
            else:
                index_u = min(length_u, 4)
            if shape.formInU() != 3 and joint_u in [0, len(us) - 1]:
                default_u = [0.8, 0.5, 0.2, 0.05, 0]
            else:
                default_u = [0.6, 0.45, 0.2, 0.05, 0]
            weights.append(default_u[index_u])
    skin_cluster.setWeights(polygon.getShape(), range(len(joints)), weights)