# coding:utf-8

from PySide import QtGui, QtCore
import pymel.core as pm
import os
import solver
import context
import tools
import curve
import surface
reload(context)
reload(solver)
reload(tools)


def bezier_v(p, t):
    return p[0]*(1-t)**3 + 3*p[1]*t*(1-t)**2 + 3*p[2]*t**2*(1-t) + p[3]*t**3


class Bezier(QtGui.QWidget):
    valueChanged = QtCore.Signal()

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
        self.__movePoint = 0
        self.__mirror = False
        self.__adsorb = False

    def resizeEvent(self, event):
        if self.height() != self.width():
            self.setMinimumHeight(self.width())

    def paintEvent(self, event):
        QtGui.QWidget.paintEvent(self, event)
        painter = QtGui.QPainter(self)
        # background
        painter.setBrush(QtGui.QBrush(QtGui.QColor(120, 120, 120), QtCore.Qt.SolidPattern))
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        # curve
        painter.setBrush(QtGui.QBrush(QtGui.QColor(100, 100, 100), QtCore.Qt.SolidPattern))
        points = [QtCore.QPointF((self.width()-1) * p[0], (self.height()-1) * p[1]) for p in self.points]
        path = QtGui.QPainterPath()
        path.moveTo(0, self.height()-1)
        path.lineTo(points[0])
        path.cubicTo(*points[1:])
        path.lineTo(self.width()-1, self.height()-1)
        painter.drawPath(path)
        # grid
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 1, QtCore.Qt.DotLine))
        w_step = (self.width()-1)/6.0
        h_step = (self.height()-1)/6.0
        for i in range(1, 6):
            w = w_step * i
            h = h_step * i
            painter.drawLine(w, 0, w, self.height())
            painter.drawLine(0, h, self.width(), h)
        # control point
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200), QtCore.Qt.SolidPattern))
        painter.drawEllipse(points[1], 6, 6)
        painter.drawEllipse(points[2], 6, 6)
        # edge
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1, QtCore.Qt.SolidLine))
        edge_points = []
        for w, h in zip([0, 0, 1, 1, 0], [0, 1, 1, 0, 0]):
            p = QtCore.QPointF(w*(self.width()-1), h*(self.height()-1))
            edge_points.extend([p, p])
        painter.drawLines(edge_points[1:-1])
        # control line
        painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 1, QtCore.Qt.DashLine))
        painter.drawLine(points[0], points[1])
        painter.drawLine(points[3], points[2])
        painter.end()

    def mousePressEvent(self, event):
        self.setFocus()
        QtGui.QWidget.mousePressEvent(self, event)
        points = [QtCore.QPointF((self.width() - 1) * p[0], (self.height() - 1) * p[1]) for p in self.points]
        p = QtCore.QPointF(event.pos())-points[1]
        length = (p.x()**2 + p.y()**2)**0.5
        if length < 6:
            self.__movePoint = 1
            return
        p = QtCore.QPointF(event.pos()) - points[2]
        length = (p.x() ** 2 + p.y() ** 2) ** 0.5
        if length < 6:
            self.__movePoint = 2
            return
        self.__movePoint = 0

    def mouseMoveEvent(self, event):
        QtGui.QWidget.mouseMoveEvent(self, event)
        if self.__movePoint == 1:
            p = QtCore.QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*12)/12.0
                y = round(y*12)/12.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[2] = [mx, my]
            self.points[1] = [x, y]
            self.update()
            self.valueChanged.emit()
        if self.__movePoint == 2:
            p = QtCore.QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*6)/6.0
                y = round(y*6)/6.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[1] = [mx, my]
            self.points[2] = [x, y]
            self.update()
            self.valueChanged.emit()

    def keyPressEvent(self, event):
        QtGui.QWidget.keyPressEvent(self, event)
        if event.key() == QtCore.Qt.Key_X:
            self.__adsorb = True
        if event.modifiers() == QtCore.Qt.ControlModifier:
            self.__mirror = True

    def keyReleaseEvent(self, event):
        QtGui.QWidget.keyReleaseEvent(self, event)
        self.__mirror = False
        self.__adsorb = False


class FloatSliderGroup(QtGui.QHBoxLayout):
    valueChange = QtCore.Signal(float)

    def __init__(self):
        QtGui.QHBoxLayout.__init__(self)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.spin = QtGui.QDoubleSpinBox()
        self.addWidget(self.spin)
        self.addWidget(self.slider)
        self.set_range(0, 1)
        self.spin.valueChanged.connect(self.convert_slider)
        self.slider.valueChanged.connect(self.convert_spin)
        self.spin.setSingleStep(0.01)
        self.spin.setDecimals(3)

    def convert_spin(self, value):
        self.spin.setValue(value/1000.0)
        self.valueChange.emit(self.spin.value())

    def convert_slider(self, value):
        self.slider.setValue(int(round(1000*value)))

    def set_range(self, min_value, max_value):
        self.spin.setRange(min_value, max_value)
        self.slider.setRange(min_value*1000, max_value*1000)

    def value(self):
        return self.spin.value()

    def set_value(self, value):
        self.spin.setValue(value)


class Solve(QtGui.QGroupBox):

    def __init__(self):
        QtGui.QGroupBox.__init__(self, "solve")
        self.args = None
        self.solve = solver.ik_solve
        self.get_args = solver.get_ik_args

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self.bezier = Bezier()
        layout.addWidget(self.bezier)

        argument_form = QtGui.QFormLayout()
        layout.addLayout(argument_form)
        self.mode = QtGui.QCheckBox()
        argument_form.addRow(u"实时模式:", self.mode)

        self.type = QtGui.QButtonGroup()
        radio_layout = QtGui.QGridLayout()
        for i, text in enumerate([u"IK", u"tall", u"soft"]):
            radio = QtGui.QRadioButton(text)
            self.type.addButton(radio, i)
            radio_layout.addWidget(radio, i/3, i % 3, 1, 1)
        self.type.button(0).setChecked(True)
        argument_form.addRow(u"解算类型:", radio_layout)

        self.radius = FloatSliderGroup()
        self.radius.set_range(0, 2)
        self.radius.set_value(1)
        argument_form.addRow(u"半径:", self.radius)
        
        paint_button = QtGui.QPushButton(u"解算")
        layout.addWidget(paint_button)

        paint_button.clicked.connect(self.apply)
        self.type.buttonClicked[int].connect(self.type_changed)
        self.mode.stateChanged.connect(self.real_time)
        self.radius.valueChange.connect(self.args_changed)
        self.bezier.valueChanged.connect(self.args_changed)

    def apply(self):
        radius = self.radius.value()
        points = self.bezier.points
        args = self.get_args()
        if args is not None:
            self.solve(points, radius, *args)

    def type_changed(self):
        self.mode.setChecked(False)
        self.radius.set_value(1)
        if self.type.checkedId() == 0:
            self.solve = solver.ik_solve
            self.get_args = solver.get_ik_args
            self.bezier.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
            self.bezier.update()
            self.mode.setEnabled(True)
        elif self.type.checkedId() == 1:
            self.solve = solver.paint_spine
            self.get_args = solver.get_args
            self.bezier.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
            self.bezier.update()
            self.mode.setEnabled(False)
        elif self.type.checkedId() == 2:
            self.solve = solver.soft_solve
            self.get_args = solver.get_soft_args
            self.bezier.points = [[0.0, 0.0], [1.0 / 3, 0.0], [2.0 / 3, 1.0], [1.0, 1.0]]
            self.bezier.update()
            self.mode.setEnabled(True)

    def args_changed(self):
        if self.mode.isChecked():
            if self.args is not None:
                radius = self.radius.value()
                points = self.bezier.points
                self.solve(points, radius, *self.args)

    def real_time(self, checked):
        if checked:
            self.args = self.get_args()
        else:
            self.args = None


class Paint(QtGui.QGroupBox):
    def __init__(self):
        QtGui.QGroupBox.__init__(self, "quickPaint")
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        from_layout = QtGui.QFormLayout()
        self.radio_groups = QtGui.QButtonGroup()
        radio_layout = QtGui.QGridLayout()
        for i, text in enumerate([u"替换", u"添加", u"放大", u"平滑",  u"减少",  u"缩小"]):
            radio = QtGui.QRadioButton(text)
            self.radio_groups.addButton(radio, i)
            radio_layout.addWidget(radio, i/3, i % 3, 1, 1)
        self.radio_groups.button(0).setChecked(True)
        from_layout.addRow(u"类型：", radio_layout)

        self.opacity = FloatSliderGroup()
        from_layout.addRow(u"透明：", self.opacity)
        layout.addLayout(from_layout)
        self.opacity.set_value(1)

        self.value = FloatSliderGroup()
        from_layout.addRow(u"数值：", self.value)
        layout.addLayout(from_layout)
        self.value.set_value(1)

        flood = QtGui.QPushButton(u"全部")
        layout.addWidget(flood)

        self.radio_groups.buttonClicked.connect(self.value_change)
        self.opacity.valueChange.connect(self.value_change)
        self.value.valueChange.connect(self.value_change)
        flood.clicked.connect(context.flood)

    def value_change(self):
        typ = self.radio_groups.checkedId()
        opacity = self.opacity.value()
        value = self.value.value()
        context.set_skin_context(typ, opacity, value)


class Rig(QtGui.QGroupBox):
    def __init__(self):
        QtGui.QGroupBox.__init__(self, "Rig")
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        from_layout = QtGui.QFormLayout()
        layout.addLayout(from_layout)

        self.type = QtGui.QButtonGroup()
        radio_layout = QtGui.QGridLayout()
        for i, text in enumerate([u"tall", u"ball", u"belt", u"cloth"]):
            radio = QtGui.QRadioButton(text)
            self.type.addButton(radio, i)
            radio_layout.addWidget(radio, i/2, i % 2, 1, 1)
        self.type.button(0).setChecked(True)
        from_layout.addRow(u"类型：", radio_layout)

        self.prefix = QtGui.QLineEdit()
        self.prefix.setText(u"prefix")
        from_layout.addRow(u"前缀：", self.prefix)

        self.inBetween = QtGui.QSpinBox()
        self.inBetween.setRange(1, 10)
        from_layout.addRow(u"插入：", self.inBetween)

        apply_button = QtGui.QPushButton(u"绑定")
        apply_button.clicked.connect(self.apply)
        layout.addWidget(apply_button)

    def apply(self):
        prefix = self.prefix.text()
        number = self.inBetween.value()
        typ = self.type.checkedId()
        spine, ball, belt, cloth = range(4)
        if typ == spine:
            curve.tail_rig(prefix, number)
        elif typ == ball:
            curve.ball_rig(prefix, number)
        elif typ == belt:
            surface.belt_rig(prefix, number)
        elif typ == cloth:
            surface.cloth_rig(prefix, number)


class Tool(QtGui.QGroupBox):
    def __init__(self):
        QtGui.QGroupBox.__init__(self, "tools")
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.tool = QtGui.QListWidget()
        self.tool.setViewMode(self.tool.IconMode)
        self.tool.setResizeMode(self.tool.Adjust)
        self.tool.setMovement(self.tool.Static)
        self.tool.setIconSize(QtCore.QSize(64, 64))
        self.tool.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tool.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.tool)
        icon_label_fun = [
            ["copySkinWeight.png", u"拷贝权重", tools.copy_weights,],
            ["exportSmoothSkin.png", u"保存权重", tools.copy_paint_widgets,],
            ["importSmoothSkin.png", u"刷入权重", tools.paste_paint_widgets,],
            ["polyEdgeToCurves.png", u"提取曲线", tools.poly_to_edge, ],
            ["rebuildCurve.png", u"重构曲线", pm.mel.RebuildCurveOptions, ],
            ["reverse.png", u"反转曲线", pm.mel.ReverseCurveOptions, ],
            ["splineHandle.png", u"重构骨骼", tools.rebuild_joint, ],
            ["extrude.png", u"脊椎简模", tools.make_select_curve_low, ],
            ["loft.png", u"放样曲面", pm.mel.LoftOptions, ],
            ["rebuildSurface.png", u"重构曲面", pm.mel.RebuildSurfacesOptions, ],
            ["toggleAxis.png", u"曲面轴向", tools.surface_axis, ],
            ["reverseSurface.png", u"反转曲面", pm.mel.ReverseSurfaceDirectionOptions, ],
        ]
        root = os.path.realpath(__file__+"/../icons")
        for icon, label, fun in icon_label_fun:
            icon = QtGui.QIcon(os.path.join(root, icon))
            item = QtGui.QListWidgetItem(icon, label)
            item.fun = fun
            self.tool.addItem(item)
        self.tool.itemClicked.connect(self.apply)

    @staticmethod
    def apply(item):
        item.fun()


class Main(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setFixedWidth(229)
        self.setObjectName(u"QuickPaint")
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(Tool())
        layout.addWidget(Solve())
        layout.addWidget(Paint())
        layout.addWidget(Rig())


window = None


def show():
    global window
    if window is None:
        if pm.dockControl("QuickPaintTool", ex=1):
            pm.deleteUI("QuickPaintTool")
        window = Main()
        pm.dockControl("QuickPaintTool", area='right', content=window.objectName(), allowedArea=['right', 'left'])
    pm.dockControl("QuickPaintTool", e=1, vis=0)
    pm.dockControl("QuickPaintTool", e=1, vis=1)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    window = Main()
    window.show()
    app.exec_()
