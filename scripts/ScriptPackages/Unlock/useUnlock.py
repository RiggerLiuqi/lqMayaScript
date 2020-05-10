# -*- coding: utf-8 -*-#
# -------------------------------------------------------------------------------#
# .@FileName:    useUnlock
# .@Author:      CousinRig67
# .@Date:        2019-12-27
# .@Contact:     842076056@qq.com
# -------------------------------------------------------------------------------#

# -*- coding: utf-8 -*-
# 解锁锁定物体
# designed by Jiaguobao
# QQ:779188083 && Tel:15615026078
# Date:2018年10月28日
# 场景里面有物体删不掉，无法重命名，（如果不是re进来的文件）估计是锁定了，执行脚本解锁物体
import pymel.core as pm
from maya.OpenMaya import MGlobal
def unLock():
	a=pm.ls()
	for i in a:
		i.unlock()
	MGlobal.displayInfo(u'unlock Finish！')
if __name__ == '__main__':
	unLock()
	print 'ok'
