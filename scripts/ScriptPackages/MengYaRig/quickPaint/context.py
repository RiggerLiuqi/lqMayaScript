# coding:utf-8

import pymel.core as pm

replace, add, scaleOut, smooth, sub, scaleIn,  = range(6)

# u"替换", u"添加", u"放大", u"平滑",  u"减少",  u"缩小"


def set_skin_context(typ, opacity, value):

    if pm.mel.currentCtx() != "artAttrSkinContext":
        return pm.warning("you must use paint skin weights tool")
    # sao
    if typ == replace:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, sao="absolute")
    if typ == smooth:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, sao="smooth")
    if typ in [add, sub]:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, sao="additive")
    if typ in [scaleIn, scaleOut]:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, sao="scale")
    # opacity
    pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, op=opacity)
    # value
    pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, miv=-1)
    pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, mxv=2)
    if typ == sub:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, val=-value)
    elif typ == scaleOut:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, val=2-value)
    else:
        pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, val=value)


def flood():
    if pm.mel.currentCtx() != "artAttrSkinContext":
        return pm.warning("you must use paint skin weights tool")
    pm.artAttrSkinPaintCtx("artAttrSkinContext", e=1, clear=True)
