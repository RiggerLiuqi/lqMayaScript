# coding:utf-8
import os
import json
try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


import pymel.core as pm
import selection
import actions
import control
import build
import weight


ROOT = os.path.abspath(os.path.join(__file__+"../.."))


def update_background():

    for hud in pm.headsUpDisplay( 'HUDObjectPosition', lh=1):
        pm.headsUpDisplay(hud, e=1, vis=False)
    path = os.path.join(ROOT, "ui",  "background")
    file_name = pm.playblast(f=path, fp=0, fmt="image", c="jpg", st=0, et=0, orn=1,
                             os=True, qlt=100, p=100, wh=(512, 640), v=0)
    if os.path.isfile(file_name.replace("####", "0")):
        if os.path.isfile(file_name.replace("####.", "")):
            os.remove(file_name.replace("####.", ""))
        os.rename(file_name.replace("####", "0"), file_name.replace("####.", ""))


def update_buttons():
    data = {}
    camera, err = actions.find_node_by_name("front")
    cp = [0, camera.ty.get(), 0]

    for attr, fun in selection.__dict__.items():
        if "Selection" not in attr:
            continue
        selection_node, err = actions.find_node_by_name(attr, False)
        if err:
            continue
        if selection_node.type() == "joint":
            p = list(selection_node.getTranslation(space="world"))
            points = [[xyz1+xyz2*0.15 for xyz1, xyz2 in zip(p, p1)]
                      for p1 in [[0, 1, 0], [1, 0, 0], [0, -1, 0], [-1, 0, 0], [0, 1, 0]]]

        else:
            points = control.get_curve_shape_points(selection_node.getShape())
        points = [[(xyz1-xyz2)/20 for xyz1, xyz2 in zip(p, cp)][:2] for p in points]
        for wh in points:
            wh[0] = (wh[0] + 0.5) * 512
            wh[1] = (0.625 - wh[1]) * 512
        whs = [[points[i], [0.5*wh1+0.5*wh2 for wh1, wh2 in zip(points[i], point)]]
               for i, point in enumerate(points[1:])]
        whs = sum(whs, [])
        whs.append(points[-1])
        data[attr] = whs
    path = os.path.join(ROOT, "ui", "buttons.json")
    with open(path, "w") as fp:
        json.dump(data, fp, indent=4)


def get_host_app():
    try:
        main_window = QApplication.activeWindow()
        while True:
            last_win = main_window.parent()
            if last_win:
                main_window = last_win
            else:
                break
        return main_window
    except:
        pass


class IconButton(QWidget):
    clicked = Signal()

    def __init__(self, parent, icon):
        QWidget.__init__(self, parent)
        self.icon = QIcon(icon)
        self.mode = QIcon.Disabled
        self.setFixedSize(36, 32)

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self.width() != self.height():
            self.setMinimumWidth(self.height())
            self.resize(self.height(), self.height())

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.icon.pixmap(self.width(), self.height(), self.mode))
        painter.end()

    def mousePressEvent(self, event):
        if self.mode == QIcon.Disabled:
            return
        self.mode = QIcon.Selected
        self.update()

    def mouseReleaseEvent(self, event):
        if self.mode == QIcon.Disabled:
            return
        self.mode = QIcon.Normal
        self.clicked.emit()
        self.update()


class FaceSelection(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setFixedSize(512, 640)
        self.pix = QPixmap(os.path.join(ROOT, "ui",  "background.jpg"))
        self.build = IconButton(self, os.path.join(ROOT, "ui",  "build.png"))
        self.build.move(512-64, 32)
        path = os.path.join(ROOT, "ui", "buttons.json")
        with open(path, "r") as fp:
            self.data = json.load(fp)
        self.name = None
        self.setMouseTracking(True)
        self.assert_build()
        self.build.clicked.connect(build.build)

    def assert_build(self):
        if all([pm.objExists(attr) for attr in self.data]):
            self.build.mode = QIcon.Normal
        else:
            self.build.mode = QIcon.Disabled

    def paintEvent(self, event):
        QDialog.paintEvent(self, event)
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.pix)
        for n, points in self.data.items():
            painter.setPen(QPen(QColor(0, 225, 225), 2, Qt.SolidLine))
            if pm.objExists(n):
                painter.setPen(QPen(QColor(0, 255, 0), 2, Qt.SolidLine))
            if self.name == n:
                painter.setPen(QPen(QColor(225, 0, 0), 2, Qt.SolidLine))
            painter.drawLines([QLineF(QPointF(*point), QPointF(*points[i]))
                               for i, point in enumerate(points[1:])])
        painter.end()

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        pos = event.pos()
        for n, points in self.data.items():
            for p in points:
                length = ((p[0] - pos.x()) ** 2 + (p[1] - pos.y()) ** 2)**0.5
                if length < 6:
                    if self.name != n:
                        self.name = n
                        self.update()
                    return
        if not (self.name is None):
            self.name = None
            self.update()

    def mousePressEvent(self, *args, **kwargs):
        if self.name is None:
            return
        if hasattr(selection, self.name):
            getattr(selection, self.name)()
        self.assert_build()
        self.update()

window = None


class Bezier(QWidget):
    valueChanged = Signal()

    def __init__(self):
        QWidget.__init__(self)
        self.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
        self.__movePoint = 0
        self.__mirror = False
        self.__adsorb = False
        print 512-2**6
        self.setFixedSize(512, 448)

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        painter = QPainter(self)
        # background
        painter.setBrush(QBrush(QColor(120, 120, 120), Qt.SolidPattern))
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        # curve
        painter.setBrush(QBrush(QColor(100, 100, 100), Qt.SolidPattern))
        points = [QPointF((self.width()-1) * p[0], (self.height()-1) * p[1]) for p in self.points]
        path = QPainterPath()
        path.moveTo(0, self.height()-1)
        path.lineTo(points[0])
        path.cubicTo(*points[1:])
        path.lineTo(self.width()-1, self.height()-1)
        painter.drawPath(path)
        # grid
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DotLine))
        w_step = (self.width()-1)/6.0
        h_step = (self.height()-1)/6.0
        for i in range(1, 6):
            w = w_step * i
            h = h_step * i
            painter.drawLine(w, 0, w, self.height())
            painter.drawLine(0, h, self.width(), h)
        # control point
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(200, 200, 200), Qt.SolidPattern))
        painter.drawEllipse(points[1], 6, 6)
        painter.drawEllipse(points[2], 6, 6)
        # edge
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        edge_points = []
        for w, h in zip([0, 0, 1, 1, 0], [0, 1, 1, 0, 0]):
            p = QPointF(w*(self.width()-1), h*(self.height()-1))
            edge_points.extend([p, p])
        painter.drawLines(edge_points[1:-1])
        # control line
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
        painter.drawLine(points[0], points[1])
        painter.drawLine(points[3], points[2])
        painter.end()

    def mousePressEvent(self, event):
        self.setFocus()
        QWidget.mousePressEvent(self, event)
        points = [QPointF((self.width() - 1) * p[0], (self.height() - 1) * p[1]) for p in self.points]
        p = QPointF(event.pos())-points[1]
        length = (p.x()**2 + p.y()**2)**0.5
        if length < 10:
            self.__movePoint = 1
            return
        p = QPointF(event.pos()) - points[2]
        length = (p.x() ** 2 + p.y() ** 2) ** 0.5
        if length < 10:
            self.__movePoint = 2
            return
        self.__movePoint = 0

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        if self.__movePoint == 1:
            p = QPointF(event.pos())
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
            p = QPointF(event.pos())
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
        QWidget.keyPressEvent(self, event)
        if event.key() == Qt.Key_X:
            self.__adsorb = True
        if event.modifiers() == Qt.ControlModifier:
            self.__mirror = True

    def keyReleaseEvent(self, event):
        QWidget.keyReleaseEvent(self, event)
        self.__mirror = False
        self.__adsorb = False


class FloatSliderGroup(QHBoxLayout):
    valueChange = Signal(float)

    def __init__(self):
        QHBoxLayout.__init__(self)
        self.slider = QSlider(Qt.Horizontal)
        self.spin = QDoubleSpinBox()
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


class FaceWeight(QWidget):

    def __init__(self):
        QWidget.__init__(self, get_host_app(), 1)
        self.kwargs = None
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(1, 1, 1, 1)
        self.bezier = Bezier()
        layout.addWidget(self.bezier)
        layout.addStretch()
        h_layout = QHBoxLayout()
        layout.addLayout(h_layout)
        h_layout.addStretch()
        argument_form = QFormLayout()
        h_layout.addLayout(argument_form)
        h_layout.addStretch()

        self.type = QButtonGroup()
        radio_layout = QGridLayout()
        for i, text in enumerate([u"次级", u"关节", u"横向拆分",
                                  u"多次级", u"多关节",  u"循环边"]):
            radio = QRadioButton(text)
            self.type.addButton(radio, i)
            radio_layout.addWidget(radio, i / 3, i % 3, 1, 1)
        self.type.button(0).setChecked(True)
        argument_form.addRow(u"类型：", radio_layout)

        self.mode = QCheckBox()
        argument_form.addRow(u"实时：", self.mode)

        self.direction = QButtonGroup()
        radio_layout = QGridLayout()
        for i, text in enumerate([u"x", u"y", u"z", u"none"]):
            radio = QRadioButton(text)
            self.direction.addButton(radio, i)
            radio_layout.addWidget(radio, 0, i, 1, 1)
        self.direction.button(0).setChecked(True)
        argument_form.addRow(u"轴向：", radio_layout)

        self.radius = FloatSliderGroup()
        self.radius.set_range(0, 3)
        self.radius.set_value(1)
        argument_form.addRow(u"半径：", self.radius)

        layout.addStretch()
        button = QPushButton(u"解算")
        layout.addWidget(button)

        self.type.buttonClicked.connect(self.type_changed)
        self.mode.stateChanged.connect(self.real_time)
        self.radius.valueChange.connect(self.args_changed)
        self.bezier.valueChanged.connect(self.args_changed)
        button.clicked.connect(self.apply)

    def type_changed(self):
        self.mode.setChecked(Qt.Unchecked)

    def args_changed(self):
        if not self.mode.isChecked():
            return
        self.solve()

    def real_time(self, checked):
        if checked:
            self.kwargs = weight.solve_kwargs(self.type.checkedId(), self.direction.checkedId())
            self.solve()
        else:
            self.kwargs = None

    def apply(self):
        if not self.mode.isChecked():
            self.kwargs = weight.solve_kwargs(self.type.checkedId(), self.direction.checkedId())
        self.solve()

    def solve(self):
        if self.kwargs is None:
            return
        i = self.type.checkedId()
        r = self.radius.value()
        d = self.direction.checkedId()
        xs, ys = zip(*self.bezier.points)
        ys = [1-y for y in ys]
        self.kwargs.update(**locals())
        weight.solve(**self.kwargs)


qss = u"""
QWidget{
    font-size: 14px;
    font-family: 楷体;
} 
"""


class FaceMain(QDialog):
    def __init__(self):
        QDialog.__init__(self, get_host_app(), 1)
        self.setStyleSheet(qss)
        self.setWindowTitle("Face")
        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)

        menu_bar = QMenuBar()
        layout.setMenuBar(menu_bar)
        tool = menu_bar.addMenu(u"工具")
        tool.addAction(u"更新次级", actions.update_second)
        tool.addAction(u"控制器显示", actions.update_second)
        tool.addAction(u"眼皮放样", actions.loft_eyelid)

        table = QTabWidget()
        layout.addWidget(table)
        table.addTab(FaceSelection(), u"创建")
        table.addTab(FaceWeight(), u"权重")

weight_window = None


def weight_show():
    global weight_window
    if window is None:
        weight_window = FaceWeight()
        weight_window.setWindowTitle("bezierWeight")
        weight_window.setStyleSheet(qss)
        weight_window.bezier.setFixedSize(512, 512)
        weight_window.setFixedHeight(700)
        weight_window.show()


def show():
    global window
    if window is None:
        window = FaceMain()
    window.show()



