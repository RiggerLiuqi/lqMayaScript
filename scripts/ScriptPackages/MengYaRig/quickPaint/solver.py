# coding:utf-8
import pymel.core as pm


def bezier_v(p, t):
    return p[0]*(1-t)**3 + 3*p[1]*t*(1-t)**2 + 3*p[2]*t**2*(1-t) + p[3]*t**3


def bezier_t(p, v):
    min_t = 0.0
    max_t = 1.0
    while True:
        t = (min_t+max_t)/2
        error_range = bezier_v(p, t) - v
        if error_range > 0.0001:
            max_t = t
        elif error_range < -0.0001:
            min_t = t
        else:
            return t


def get_widget(points, x):
    if x <= 0:
        return points[0][1]
    elif x >= 1:
        return points[3][1]
    t = bezier_t([p[0] for p in points], x)
    return bezier_v([p[1] for p in points], t)


def get_soft_args():
    selected = pm.selected(o=1, type="mesh")
    if not len(selected) == 1:
        return pm.warning("please select component")
    mesh = selected[0]
    skin_clusters = mesh.listHistory(type="skinCluster")
    if not skin_clusters:
        return pm.warning("can not find skinCluster")
    skin_cluster = skin_clusters[0]
    pm.softSelect(sse=1)
    pm.softSelect(ssc="0,1,1,1,0,1")
    radius = pm.softSelect(q=1, ssd=1)
    pm.softSelect(ssd=radius * 2)
    old_points = mesh.getPoints(space="world")
    pm.move([0, 1, 0], r=1)
    new_points = mesh.getPoints(space="world")
    pm.move([0, -1, 0], r=1)
    pm.softSelect(ssd=radius)
    distances = [(new[1] - old[1]) for old, new in zip(old_points, new_points)]
    return skin_cluster, distances


def soft_solve(points, radius, skin_cluster, distances):
    points = [list(point) for point in points]
    for point in points:
        point[1] = 1-point[1]
    xs = [(1-d)*2/radius for d in distances]
    weights = [get_widget(points, x) for x in xs]
    skin_cluster.paintWeights.set(weights)


def get_ik_args():
    selected = pm.selected(type="transform")
    if not len(selected) == 1:
        return pm.warning("please select polygon")
    polygon = selected[0]
    mesh = polygon.getShape()
    if mesh is None:
        return pm.warning("please select polygon")
    if mesh.type() != "mesh":
        return pm.warning("please select polygon")
    skin_clusters = mesh.listHistory(type="skinCluster")
    if not skin_clusters:
        return pm.warning("can not find skinCluster")
    skin_cluster = skin_clusters[0]
    paint_joints = [joint for joint in skin_cluster.paintTrans.inputs() if joint.type() == "joint"]
    if len(paint_joints) != 1:
        return pm.mel.warning("\nyou need a quickPaint joint")
    paint_joint = paint_joints[0]
    unlock_joints = [joint for joint in skin_cluster.getInfluence() if joint.type() == "joint" and not joint.liw.get()]
    if len(unlock_joints) != 1:
        return pm.mel.warning("\nyou need a unlock joint")
    unlock_joint = unlock_joints[0]
    local_tx = (pm.datatypes.Point(paint_joint.getTranslation(space="world"))*unlock_joint.getMatrix(ws=1).inverse())[0]
    if local_tx > 0:
        direction = 1
    else:
        direction = -1
    xs = []
    unlock_inverse = unlock_joint.getMatrix(ws=1).inverse()
    paint_inverse = paint_joint.getMatrix(ws=1).inverse()
    for point in mesh.getPoints(space="world"):
        x1 = (point*unlock_inverse)[0]-local_tx
        x2 = (point*paint_inverse)[0]
        xs.append((x1+x2)/2*direction)
    return skin_cluster, xs


def ik_solve(points, radius, skin_cluster, xs):
    points = [list(point) for point in points]
    for point in points:
        point[1] = 1-point[1]
    radius = pm.softSelect(q=1, ssd=1)*radius
    xs = [x/radius/2+0.5 for x in xs]
    weights = [get_widget(points, x) for x in xs]
    skin_cluster.paintWeights.set(weights)


def get_args():
    return []


def paint_spine(points, radius):
    points = [list(point) for point in points]
    for point in points:
        point[1] = 1-point[1]
    radius = pm.softSelect(q=1, ssd=1) * radius
    selected = pm.selected(type="transform")
    if not len(selected) == 1:
        return pm.warning("please select polygon")
    polygon = selected[0]
    mesh = polygon.getShape()
    if mesh is None:
        return pm.warning("please select polygon")
    if mesh.type() != "mesh":
        return pm.warning("please select polygon")
    skin_clusters = mesh.listHistory(type="skinCluster")
    if not skin_clusters:
        return pm.warning("can not find skinCluster")
    skin_cluster = skin_clusters[0]
    ids = []
    joints = []
    for i, joint in enumerate(skin_cluster.getInfluence()):
        if not joint.liw.get():
            ids.append(i)
            joints.append(joint)
    old_weight_matrix = [list(skin_cluster.getWeights(mesh, i)) for i in ids]
    max_weights = [sum(ws) for ws in zip(*old_weight_matrix)]
    weight_matrix = [max_weights]
    polygon_points = mesh.getPoints(space="world")
    for i, paint_joint in enumerate(joints[1:]):
        unlock_joint = joints[i]
        local_tx = \
        (pm.datatypes.Point(paint_joint.getTranslation(space="world")) * unlock_joint.getMatrix(ws=1).inverse())[0]
        if local_tx > 0:
            direction = 1
        else:
            direction = -1
        xs = []
        unlock_inverse = unlock_joint.getMatrix(ws=1).inverse()
        paint_inverse = paint_joint.getMatrix(ws=1).inverse()
        for point in polygon_points:
            x1 = (point * unlock_inverse)[0] - local_tx
            x2 = (point * paint_inverse)[0]
            xs.append((x1 + x2) / 2 * direction)
        xs = [x / radius / 2 + 0.5 for x in xs]
        weights = [get_widget(points, x) for x in xs]
        weights = [min(w1, w2) for w1, w2 in zip(weight_matrix[-1], weights)]
        weight_matrix.append(weights)
        weight_matrix[-2] = [w2-w1 for w1, w2 in zip(weight_matrix[-1], weight_matrix[-2])]
    weights = sum([list(ws) for ws in zip(*weight_matrix)], [])
    skin_cluster.setWeights(mesh, ids, weights)
    paint_joints = [joint for joint in skin_cluster.paintTrans.inputs() if joint.type() == "joint"]
    if len(paint_joints) != 1:
        return pm.mel.warning("\nyou need a quickPaint joint")
    paint_joint = paint_joints[0]
    skin_cluster.paintWeights.set(weight_matrix[joints.index(paint_joint)])
