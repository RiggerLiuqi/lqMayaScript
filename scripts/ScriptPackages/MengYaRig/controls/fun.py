import json
import os

import pymel.core as pm

ROOT = os.path.abspath(os.path.join(__file__+"../.."))


def export_controls():
    selected = pm.selected(o=1)
    if len(selected) != 1:
        return pm.warning("you should select a curve")
    curve = selected[0]
    if curve.type() != "transform":
        return pm.warning("you should select a curve")
    curve_shape = curve.getShape()
    if not curve_shape:
        return pm.warning("you should select a curve")
    if curve_shape.type() != "nurbsCurve":
        return pm.warning("you should select a curve")
    return curve_shape





