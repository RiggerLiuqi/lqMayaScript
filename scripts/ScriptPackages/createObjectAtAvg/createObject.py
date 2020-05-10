# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    createObject
# .@Author:      CousinRig67
# .@Date:        2020-04-20
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

import pymel.core as pm


def craObjAtAvg():
    '''
    'Object@Average' MEL script

    Author: Carlos Rico Adega - carlos.rico.3d@gmail.com

    Copyright ?2017 Carlos Rico Adega

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.


    SCRIPT NAME:
        craObjAtAvg.mel

        Main procedure:
            craObjAtAvgCmd;

    DESCRIPTION:
            Object At Average Position.

    LAUNCH UI:
        craObjAtAvg;

    CHANGE LOG:
            Version: 2.0.0
            Date: OCtober 30, 2017
                - Option to work on individual selections rather than average
                - Option to parent to source object
                - Option to orient objects to surface normal
                - Option to create transform stack to zero out object transforms
                - Tool name change
                - Grouping of objects under 'objectAtAverage_grp'
                - Options saved in optionVars
                - Redesigned UI

            Version: 1.0.0
            Date: July 23, 2015
                - First release
    '''

    if not pm.optionVar(exists = 'craObjAtAvgForEachItemOV'):
        pm.optionVar(iv = ('craObjAtAvgForEachItemOV', 0))

    if not pm.optionVar(exists = 'craObjAtAvgOrientToNormalOV'):
        pm.optionVar(iv = ('craObjAtAvgOrientToNormalOV', 0))

    if not pm.optionVar(exists = 'craObjAtAvgZeroOutXformsOV'):
        pm.optionVar(iv = ('craObjAtAvgZeroOutXformsOV', 0))

    if not pm.optionVar(exists = 'craConstrainObjectsOV'):
        pm.optionVar(iv = ('craConstrainObjectsOV', 0))

    nodes = ["circle", "camera", "joint", "locator", "pointLight", "polyCone", "polyCube", "polySphere", "sphere"]
    if pm.window('craObjectAtAveragePosWin', exists = 1):
        pm.deleteUI('craObjectAtAveragePosWin')

    pm.window('craObjectAtAveragePosWin', tlb = 0, mnb = 0, mxb = 0, t = "Object@Average", s = 0)
    pm.frameLayout(lv = 0, mw = 4, mh = 4)
    pm.columnLayout(adj = 1)
    pm.rowLayout(h = 30, nc = 4, adj = 2, bgc = (.6, .6, .6))
    # text -l "<font color=lightblue><b>&nbsp;Type&nbsp;</b></font>";
    pm.text(l = " Type", w = 28)
    pm.optionMenu('craObjectToAveragePosOM', h = 20, ann = (str(len(nodes)) + " types"), bgc = (.4, .4, .4))
    for node in nodes:
        pm.menuItem((str(node) + "MI"),
                    l = node)

    if pm.mel.getApplicationVersionAsFloat() > 2015:
        pm.iconTextButton(i = "help.png", h = 20, ann = "About", c = lambda *args: pm.mel.craObjAtAvgAbout(), w = 20)


    else:
        pm.iconTextButton(i = "pickOtherObj.png", h = 20, ann = "About", c = lambda *args: pm.mel.craObjAtAvgAbout(),
                          w = 20)

    pm.text(l = "", w = 1)
    pm.setParent('..')
    pm.separator(h = 5, st = "none")
    pm.rowLayout(h = 26, bgc = (.4, .2, .2), adj = 2, nc = 2)
    pm.text(l = "  ")
    pm.checkBox('craForEachObjectsCB', cc = lambda *args: pm.optionVar(iv = ('craObjAtAvgForEachItemOV', args[0])),
                onc = lambda *args: pm.mel.craInViewMessage("For each item",
                                                            "Create an object per each selected item position, not the average"),
                ann = "Create an object per each selected item position, not the average",
                l = "For each selected",
                v = pm.optionVar(q = 'craObjAtAvgForEachItemOV'))
    pm.setParent('..')
    pm.rowLayout(h = 24, bgc = (.2, .4, .2), adj = 2, nc = 2)
    pm.text(l = "  ")
    pm.checkBox('craConstrainObjectsCB', cc = lambda *args: pm.optionVar(iv = ('craConstrainObjectsOV', args[0])),
                onc = lambda *args: pm.mel.craInViewMessage("Constrain objects",
                                                            "Parent constrain object(s) to source objects"),
                ann = "Constrain object(s)",
                l = "Parent to selection",
                v = pm.optionVar(q = 'craConstrainObjectsOV'))
    pm.setParent('..')
    pm.rowLayout(h = 24, bgc = (.4, .4, .2), adj = 2, nc = 2)
    pm.text(l = "  ")
    pm.checkBox('craOrientObjectsCB', cc = lambda *args: pm.optionVar(iv = ('craObjAtAvgOrientToNormalOV', args[0])),
                onc = lambda *args: pm.mel.craInViewMessage("Orient to normal",
                                                            "Orient object(s) to the surface normal of the components"),
                ann = "Orient object(s) to the surface normal of the components",
                l = "Use surface normal",
                v = pm.optionVar(q = 'craObjAtAvgOrientToNormalOV'))
    pm.setParent('..')
    pm.rowLayout(h = 24, bgc = (.2, .4, .4), adj = 2, nc = 2)
    pm.text(l = "  ")
    pm.checkBox('craZeroOutObjectCB', cc = lambda *args: pm.optionVar(iv = ('craObjAtAvgZeroOutXformsOV', args[0])),
                onc = lambda *args: pm.mel.craInViewMessage("Zero out transforms",
                                                            "Make transform stack to zero out the newly created object(s)"),
                ann = "Make transform stack to zero out the newly created object(s)",
                l = "Zero out transforms",
                v = pm.optionVar(q = 'craObjAtAvgZeroOutXformsOV'))
    pm.setParent('..')
    # setParent ..;
    pm.separator(h = 5, st = "none")
    pm.button('craObjAtAvgCmdBTN', h = 24,
              ann = "Creates an object at the average position of selected items",
              bgc = (.6, .6, .6),
              l = "Place object(s)",
              c = lambda *args: pm.mel.craObjAtAvgCmdWrapper())
    pm.setParent('..')
    pm.setParent('..')
    pm.optionMenu('craObjectToAveragePosOM', e = 1, v = "locator")
    if pm.mel.getApplicationVersionAsFloat() > 2015:
        pm.window('craObjectAtAveragePosWin', e = 1, wh = (153, 172))


    else:
        pm.window('craObjectAtAveragePosWin', e = 1, wh = (153, 174))

    pm.setFocus('craObjAtAvgCmdBTN')
    pm.showWindow('craObjectAtAveragePosWin')


def craObjAtAvgCmdWrapper():
    origObjs = pm.ls(fl = 1, sl = 1)
    newObjs = []
    if pm.checkBox('craForEachObjectsCB', q = 1, v = 1):
        for craObj in origObjs:
            pm.select(craObj, r = 1)
            newObjs.append(str(pm.mel.craObjAtAvgCmd(pm.optionMenu('craObjectToAveragePosOM', q = 1, v = 1),
                                                     pm.checkBox('craOrientObjectsCB', q = 1, v = 1),
                                                     pm.checkBox('craZeroOutObjectCB', q = 1, v = 1),
                                                     pm.checkBox('craConstrainObjectsCB', q = 1, v = 1))))



    else:
        newObjs.append(str(pm.mel.craObjAtAvgCmd(pm.optionMenu('craObjectToAveragePosOM', q = 1, v = 1),
                                                 pm.checkBox('craOrientObjectsCB', q = 1, v = 1),
                                                 pm.checkBox('craZeroOutObjectCB', q = 1, v = 1),
                                                 pm.checkBox('craConstrainObjectsCB', q = 1, v = 1))))

    pm.select(newObjs, r = 1)


def craObjAtAvgCmd(type, orient, zero, constrain):
    origObjs = pm.ls(fl = 1, sl = 1)
    if not len(pm.ls(sl = 1)):
        pm.pm.mel.error("Select at least an object")

    selObj = origObjs
    selObjParents = []
    craCount = 0
    sum = Vector([0, 0, 0])
    objPos = Vector()
    if not pm.objExists("|objectAtAverage_grp"):
        pm.group(em = 1, n = "|objectAtAverage_grp")
        pm.select(origObjs, r = 1)

    for item in selObj:
        if pm.mel.gmatch(item, "*.e*") or pm.mel.gmatch(item, "*.f*"):
            pm.select(pm.polyListComponentConversion(fuv = 1, fvf = 1, fe = 1, ff = 1, tv = 1),
                      r = 1)
            selObj = pm.ls(fl = 1, sl = 1)
            selObjParents = pm.listRelatives("-p",
                                             pm.listRelatives(p = 1),
                                             item)
            break

    craCount = len(selObj)
    for crai in selObj:
        if pm.mel.gmatch(crai, "*.vtx*") or pm.mel.gmatch(crai, "*.cv*"):
            objPos = Vector(pm.xform(crai, q = 1, ws = 1, t = 1))
            selObjParents = pm.listRelatives("-p",
                                             pm.listRelatives(p = 1),
                                             crai)


        else:
            objPos = Vector(pm.xform(crai, q = 1, rp = 1, ws = 1))

        sum += objPos

    average = sum / craCount
    pm.select(cl = 1)
    nameType = type
    type2 = ""
    if type == "locator":
        type = "spaceLocator"

        type2 = "loc"


    elif type == "circle":
        type += " -normalX 1 -normalY 0 -normalZ 0"

        type2 = "crv"


    elif type == "polyCone":
        type += " -axis 1 0 0"

        type2 = "geo"


    elif type == "joint":
        type2 = "jnt"


    elif type == "camera":
        type2 = "cam"


    elif type == "pointLight":
        type2 = "lht"


    else:
        type2 = "geo"

    parents = pm.listRelatives("-p",
                               pm.ls(selObj[0], o = 1))
    if not len(parents):
        parents[0] = origObjs[0]

    newObj = []
    if type != "joint" and type != "pointLight":
        newObj = pm.mel.eval(type + "-n " + (parents[0] + "_" + type2))


    else:
        newPosition = pm.mel.eval(type + "-n " + (parents[0] + "_" + type2))
        newObj[0] = str(newPosition)
        if type == "pointLight":
            parents = pm.listRelatives(("|" + parents[0] + "_" + type2 + "|" + str(newPosition)),
                                       p = 1, f = 1)
            newObj[0] = parents[0]

    created = newObj[0]
    pm.pm.cmds.move((average.x), (average.y), (average.z))
    newObjGrp = ""
    if orient:
        pm.catch(lambda: pm.delete(pm.normalConstraint(origObjs,
                                                       ("|" + created),
                                                       worldUpType = "vector", aimVector = (1, 0, 0),
                                                       upVector = (0, 1, 0), weight = 1, worldUpVector = (0, 1, 0))))

    if type == "joint":
        pm.makeIdentity(created, n = 0, s = 1, r = 1, t = 1, apply = True, pn = 1)

    if zero:
        created = str(pm.mel.craZeroOutObjectGrp("|" + created))


    else:
        createdName = pm.parent(("|" + created), 'objectAtAverage_grp')
        created = str(createdName[0])

    if constrain:
        allParents = origObjs
        if len(selObjParents):
            allParents = selObjParents + origObjs

        pm.parentConstraint(allParents, created, mo = 1)

    if zero:
        sel = pm.ls(l = 1, sl = 1)
        return sel[0]


    else:
        return created


def craZeroOutObjectGrp(obj):
    parent = pm.listRelatives(obj, parent = 1)
    if not len(parent):
        parent = pm.ls(obj, o = 1, sl = 1)

    translation = pm.xform(obj, q = 1, ws = 1, t = 1)
    rotation = pm.xform(obj, q = 1, ro = 1, ws = 1)
    scale = pm.xform(obj, q = 1, s = 1, r = 1, ws = 1)
    SDKGroup = str(pm.group(em = 1, a = 1, n = (obj + "_SDK_Grp")))
    OffsetGroup = str(pm.group(SDKGroup, a = 1, parent = "objectAtAverage_grp", n = (obj + "_offset_Grp")))
    pm.xform(OffsetGroup, s = (scale[0], scale[1], scale[2]), ro = (rotation[0], rotation[1], rotation[2]), ws = 1,
             t = (translation[0], translation[1], translation[2]))
    pm.parent(obj,
              (OffsetGroup + "|" + SDKGroup))
    return OffsetGroup


def craInViewMessage(message1, message2):
    if pm.mel.getApplicationVersionAsFloat() > 2013:
        inViewStatus = int(pm.optionVar(q = 'inViewMessageEnable'))
        pm.optionVar(iv = ('inViewMessageEnable', True))
        print "\n" + message1 + " " + message2 + "\n"
        pm.inViewMessage(a = .9, bkc = 0x00001100, fadeStayTime = 1000, pos = 'midCenter', fadeOutTime = 100, fade = 1,
                         smg = (
                                     "<font color=\"orange\">" + message1 + " </font><font color=\"limegreen\">" + message2 + "</font>"),
                         fadeInTime = 100)
        pm.optionVar(iv = ('inViewMessageEnable', inViewStatus))


    else:
        print "\n" + message1 + " " + message2 + "\n"
        pm.headsUpMessage((message1 + " " + message2),
                          t = 0.1)


def craObjAtAvgAbout():
    if pm.window('craObjAtAvgAboutWin', exists = 1):
        pm.deleteUI('craObjAtAvgAboutWin')

    pm.window('craObjAtAvgAboutWin', tlb = 1, s = 0, t = "About this Tool")
    pm.frameLayout(lv = 0, mw = 5, mh = 5)
    pm.frameLayout(lv = 0, mw = 5, mh = 5)
    pm.columnLayout(adj = 1)
    pm.text(l = "<font color=gold><h3>Object@Average</h3></font>")
    pm.text(l = "<font color=steelblue><h3>v2.0.0</h3></font>")
    pm.text(l = "\nPlace object at\naverage position.\n")
    pm.text(l = "It works with\nselected transforms,\nfaces, edges,\nvertices or CVs.\n")
    pm.textField(ed = 0, text = "   carlos.rico.3d@gmail.com")
    pm.text(l = "")
    pm.text(l = "<font color=indianred><h4>Carlos Rico Adega &copy; 2017</h4></font>")
    pm.text(l = "")
    pm.rowLayout(nc = 2, adj = 1)
    pm.button(
        c = lambda *args: pm.showHelp("https://www.highend3d.com/users/charliewales/free/downloads", absolute = 1),
        ann = "Free downloads from CreativeCrash.com", l = "Downloads", w = 70)
    pm.button(c = lambda *args: pm.showHelp("https://www.linkedin.com/in/carlos-rico-adega-3250586/", absolute = 1),
              ann = "Linked[In] profile", l = "Linked[In]", w = 70)
    pm.setParent('..')
    pm.rowLayout(nc = 2, adj = 1)
    pm.button(c = lambda *args: pm.showHelp("https://vimeo.com/channels/749131", absolute = 1), ann = "Vimeo Channel",
              l = "Vimeo")
    pm.button(c = lambda *args: pm.showHelp("https://www.youtube.com/channel/UCXnSX8PHpQtwJR-uN-atO3Q", absolute = 1),
              ann = "Youtube Channel", l = "YouTube", w = 70)
    pm.setParent('..')
    pm.setParent('..')
    pm.window('craObjAtAvgAboutWin', e = 1, wh = (176, 285))
    pm.showWindow('craObjAtAvgAboutWin')



