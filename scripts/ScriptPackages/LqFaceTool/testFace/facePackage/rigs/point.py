# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    point
# .@Author:      CousinRig67
# .@Date:        2020-03-09
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

from . import Rig
import pymel.core as pm


class PointRig(Rig):
    name = 'point'

    def rig(self):

        for fit in self.fits:
                if len(self.fits) == 1 and fit.rml != 'Middle':
                    temp_group_01 = pm.group(em = 1)
                    temp_group_02 = pm.group(em = 1, p = temp_group_01)
                    temp_group_02.setMatrix(fit.node.getMatrix(ws = True), ws = True)
                    temp_group_01.sx.set(-1)
                    matrix = temp_group_02.getMatrix(ws = True)
                    pm.delete(temp_group_01)
                    prefix = '{fit.group}{fit.field}{rml}'.format(fit = fit,
                                                                  rml = {'Left':'Right', 'Right': 'Left'}[fit.rml])
                    self.point_rig(prefix, matrix)
                else:
                    prefix = '{fit.group}{fit.field}{fit.rml}'.format(fit=fit)
                    matrix = fit.node.getMatrix(ws=True)
                    self.point_rig(prefix, matrix)

    def point_rig(self, prefix, matrix):
        zero_group = pm.group(em = True, p = self.group, n = prefix + 'ZeroGroup')
        zero_group.setMatrix(matrix, ws = True)
        rig_loc= pm.group(em = True, p = zero_group, n = prefix + 'RigLocator')
        rig_locShape = pm.createNode('locator', p = rig_loc, n = prefix + 'RigLocatorShape')
        joint = pm.joint(self.joint, n = prefix + 'Joint')
        pm.parent(pm.parentConstraint(rig_loc, joint), rig_loc)
        rig_loc.s.connect(joint.s)