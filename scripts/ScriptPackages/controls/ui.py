# coding=utf-8
import os

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *


from control import Control
import pymel.core as pm


class ScaleList(QListWidget):

    def wheelEvent(self, event):
        if QApplication.keyboardModifiers() != Qt.ControlModifier:
            QListWidget.wheelEvent(self, event)
        else:
            if event.delta() > 0:
                w = min(self.iconSize().width() + 4, 128)
                self.setIconSize(QSize(w, w))
                for i in range(self.count()):
                    self.item(i).setSizeHint(QSize(w+3, w+3))
            elif event.delta() < 0:
                w = max(self.iconSize().width() - 4, 16)
                self.setIconSize(QSize(w, w))
                for i in range(self.count()):
                    self.item(i).setSizeHint(QSize(w + 3, w + 3))


class ShapeList(ScaleList):

    def __init__(self):
        ScaleList .__init__(self)
        self.update_shapes()
        self.setMovement(self.Static)
        self.setSelectionMode(self.ExtendedSelection)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(self.IconMode)
        self.setIconSize(QSize(64, 64))
        self.setResizeMode(self.Adjust)
        self.itemDoubleClicked.connect(self.double_clicked)
        self.menu = QMenu(self)
        self.menu.addAction(u"上传控制器", self.upload_control)
        self.menu.addAction(u"删除控制器", self.delete_control)
        
    def contextMenuEvent(self, event):
        QListWidget.contextMenuEvent(self, event)
        self.menu.exec_(event.globalPos())

    def update_shapes(self):
        self.clear()
        data_dir = os.path.abspath(__file__ + "/../data/")
        for file_name in os.listdir(data_dir):
            name, ext = os.path.splitext(file_name)
            if ext != ".jpg":
                continue
            jpg_file = os.path.join(data_dir, file_name)
            icon = QIcon(jpg_file)
            item = QListWidgetItem(icon, "", self)
            item.name = name
            item.setSizeHint(QSize(67, 67))

    @staticmethod
    def double_clicked(item):
        pm.undoInfo(openChunk=1)
        s = item.name
        selected = Control.selected()
        if selected:
            Control.set_selected(s=s, r=Control.get_soft_radius())
        else:
            Control(n=s, s=s, r=Control.get_soft_radius())
        pm.undoInfo(closeChunk=1)

    def upload_control(self):
        pm.undoInfo(openChunk=1)
        for control in Control.selected():
            control.upload()
        self.update_shapes()
        pm.undoInfo(closeChunk=1)

    def delete_control(self):
        pm.undoInfo(openChunk=1)
        shapes = [item.name for item in self.selectedItems()]
        Control.delete_shapes(*shapes)
        self.update_shapes()
        pm.undoInfo(closeChunk=1)


class ColorList(ScaleList):
    def __init__(self):
        ScaleList .__init__(self)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(self.IconMode)
        self.setIconSize(QSize(32, 32))
        self.setResizeMode(self.Adjust)
        self.setFixedHeight(35*4)
        index_rgb_map = [
            [0.5, 0.5, 0.5],
            [0, 0, 0],
            [0.247, 0.247, 0.247],
            [0.498, 0.498, 0.498],
            [0.608, 0, 0.157],
            [0, 0.16, 0.376],
            [0, 0, 1],
            [0, 0.275, 0.094],
            [0.149, 0, 0.263],
            [0.78, 0, 0.78],
            [0.537, 0.278, 0.2],
            [0.243, 0.133, 0.121],
            [0.6, 0.145, 0],
            [1, 0, 0],
            [0, 1, 0],
            [0, 0.2549, 0.6],
            [1, 1, 1],
            [1, 1, 0],
            [0.388, 0.863, 1],
            [0.263, 1, 0.639],
            [1, 0.686, 0.686],
            [0.89, 0.674, 0.474],
            [1, 1, 0.388],
            [0, 0.6, 0.329],
            [0.627, 0.411, 0.188],
            [0.619, 0.627, 0.188],
            [0.408, 0.631, 0.188],
            [0.188, 0.631, 0.365],
            [0.188, 0.627, 0.627],
            [0.188, 0.403, 0.627],
            [0.434, 0.188, 0.627],
            [0.627, 0.188, 0.411],
        ]
        for i, rgb in enumerate(index_rgb_map):
            pix = QPixmap(128, 128)
            pix.fill(QColor.fromRgbF(*rgb))
            item = QListWidgetItem(QIcon(pix), "", self)
            item.setSizeHint(QSize(35, 34))
        self.itemDoubleClicked.connect(self.double_clicked)

    def double_clicked(self, item):
        pm.undoInfo(openChunk=1)
        index = self.indexFromItem(item)
        c = index.row()
        Control.set_selected(c=c)
        pm.undoInfo(closeChunk=1)


def get_app():
    app = QApplication.activeWindow()
    while True:
        parent = app.parent()
        if parent:
            app = parent
        else:
            break
    return app


class ControlsWindow(QDialog):

    def __init__(self):
        QDialog .__init__(self, get_app(), 1)
        self.setWindowTitle("controls")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.resize(307, 474)
        shape_list = ShapeList()
        layout.addWidget(shape_list)

        color_list = ColorList()
        layout.addWidget(color_list)

        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        scale_button = QPushButton(u"缩放")
        mirror_button = QPushButton(u"镜像")
        replace_button = QPushButton(u"替换")
        button_layout.addWidget(scale_button)
        button_layout.addWidget(mirror_button)
        button_layout.addWidget(replace_button)

        scale_button.clicked.connect(self.scale_control)
        mirror_button.clicked.connect(self.mirror_control)
        replace_button.clicked.connect(self.replace_control)

    @staticmethod
    def scale_control():
        pm.undoInfo(openChunk=1)
        Control.set_selected(r=Control.get_soft_radius())
        pm.undoInfo(closeChunk=1)

    @staticmethod
    def mirror_control():
        pm.undoInfo(openChunk=1)
        Control.mirror_selected()
        pm.undoInfo(closeChunk=1)

    @staticmethod
    def replace_control():
        pm.undoInfo(openChunk=1)
        selected = Control.selected()
        target = selected.pop()
        shape = target.get_shape()
        for control in selected:
            control.set_shape(shape)
        pm.undoInfo(closeChunk=1)

window = None


def show():
    u"""
    显示界面:
    """
    global window
    if window is None:
        window = ControlsWindow()
    window.show()


if __name__ == '__main__':
    _app = QApplication([])
    window = ControlsWindow()
    window.show()
    _app.exec_()
