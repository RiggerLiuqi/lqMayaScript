# coding:utf-8

import os

from PySide import QtGui, QtCore

import action


class CurveList(QtGui.QListWidget):

    def __init__(self):
        QtGui.QListWidget.__init__(self)
        self.setViewMode(self.IconMode)
        self.setIconSize(QtCore.QSize(65, 65))
        self.setResizeMode(self.Adjust)
        self.setMovement(self.Static)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.reload()
        self.itemDoubleClicked.connect(self.load)
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(u"上传", self.upload)
        self.menu.addAction(u"载入", self.load)
        self.menu.addAction(u"删除", self.delete)

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def wheelEvent(self, event):
        if event.modifiers() & QtCore.Qt.CTRL:
            if event.delta() > 0:
                width = min([self.iconSize().width()+4, 128])
                self.setIconSize(QtCore.QSize(width, width))
            else:
                width = max([self.iconSize().width()-4, 16])
                self.setIconSize(QtCore.QSize(width, width))
        else:
            QtGui.QListWidget.wheelEvent(self, event)

    def reload(self):
        self.clear()
        icon_dir = os.path.join(action.ROOT, "data")
        if not os.path.isdir(icon_dir):
            return
        for basename in os.listdir(icon_dir):
            name, ext = os.path.splitext(basename)
            if ext != ".jpg":
                continue
            QtGui.QListWidgetItem(QtGui.QIcon(os.path.join(icon_dir, basename)), name, self)

    def load(self):
        action.load_curves(self.currentItem().text())

    def upload(self):
        action.upload_select_curve()
        self.reload()

    def delete(self):
        action.delete_curve(self.currentItem().text())
        self.reload()


class ColorList(QtGui.QListWidget):

    def __init__(self):
        QtGui.QListWidget.__init__(self)
        self.setViewMode(self.IconMode)
        self.setResizeMode(self.Adjust)
        self.setMovement(self.Static)
        self.setFont(QtGui.QFont("", 24, 24))
        self.setMaximumHeight(235)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
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
        for rgb in index_rgb_map:
            item = QtGui.QListWidgetItem(QtGui.QIcon(), "     ")
            item.setBackground(QtGui.QBrush(QtGui.QColor.fromRgbF(*rgb)))
            self.addItem(item)
        self.itemDoubleClicked.connect(self.set_color)

    def set_color(self):
        index = self.currentIndex().row()
        action.set_selected_curve_color(index)
        print self.currentItem().background().color().getRgbF()
        self.currentItem().setSelected(False)


class CurveMain(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self, QtGui.QApplication.activeWindow(), 1)
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        self.list = CurveList()
        layout.addWidget(self.list)
        self.color = ColorList()
        layout.addWidget(self.color)
        self.resize(362, 600)
        self.setMinimumWidth(362)
        button_layout = QtGui.QHBoxLayout()
        layout.addLayout(button_layout)
        button = QtGui.QPushButton(u"替换")
        button_layout.addWidget(button)
        button.clicked.connect(action.replace_select_curves)
        button.setFixedHeight(30)
        button = QtGui.QPushButton(u"缩放")
        button_layout.addWidget(button)
        button.clicked.connect(action.set_select_curve_radius)
        button.setFixedHeight(30)
        button = QtGui.QPushButton(u"镜像")
        button_layout.addWidget(button)
        button.clicked.connect(action.mirror_curve)
        button.setFixedHeight(30)
        button = QtGui.QPushButton(u"关闭")
        button_layout.addWidget(button)
        button.clicked.connect(self.close)
        button.setFixedHeight(30)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    ui = CurveMain()
    ui.show()
    app.exec_()
