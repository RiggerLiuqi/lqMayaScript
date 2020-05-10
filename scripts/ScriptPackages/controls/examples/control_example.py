# coding=utf-8

import pymel.core as pm
from controls.control import Control

# 偏向面向对象思路的使用方式
circle = pm.circle(ch=1)[0]
control = Control(circle)
print control
group = pm.group(em=1)
control.set_parent(group)
control.set_name("circle")
control.set_color(13)
control.set_radius(2)

# 偏向mel面向过程的使用方式
group2 = pm.group(em=1)
Control(control, p=group2, r=1.5, c=6)

# 控制器上传使用
circle2 = pm.circle(ch=1, d=1, s=6)[0]
control2 = Control(circle2)
control2.set_name("SixEdge")
control2.upload()
control.upload()
control.set_shape("SixEdge")
control2.set_shape("SixEdge")
control.set_shape("circle")
control2.set_shape("circle")

# 在绑定代码中使用Control创建控制器
con = Control(n="TestCon", s="SixEdge", r=1.5, p=group)
