#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/3 15:49
# @Author  : lockcy
# @File    : main.py
from PyQt5 import Qt
from PyQt5.QtCore import QSize, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QPushButton, QWidget, QFormLayout, QTabWidget, \
    QTreeWidgetItem, QTreeWidget, QListView, QLabel, QGraphicsScene, QGraphicsPixmapItem, QGraphicsView, QDesktopWidget
from PyQt5.QtGui import QIcon, QImage, QPixmap, QPainter, QPen
from PyQt5.QtWidgets import *
import sys
import fitz
import shutil
import os

DATA_PATH = os.path.join(os.getcwd(), 'data')
CHECK_PATH = os.path.join(DATA_PATH, 'checklist')
AIR_PATH = os.path.join(DATA_PATH, 'airport')


class EfbMain(QTabWidget):
    msg = pyqtSignal(str)

    def __init__(self, parent=None):
        super(EfbMain, self).__init__(parent)
        self.tab1 = QWidget()
        self.checkList = QWidget()
        self.CheckView = QGraphicsView()
        self.ccount=0
        self.tree = QTreeWidget()
        self.updateTree()
        self.initUi()

        self.msg.connect(self.updateGraph)

    def updateGraph(self, path):
        doc = fitz.open(path)
        page = doc.loadPage(0)
        cover = self.render_pdf_page(page, True)
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap(cover))

    def initUi(self):
        self.setWindowTitle('737ng EFB')
        self.setWindowIcon(QIcon('plane.ico'))
        self.addTab(self.tab1, '航图')
        self.addTab(self.checkList, '检查单')
        self.graphUI()
        self.checkListUI()
        self.tree.clicked.connect(self.onTreeClicked)
        self.CheckView.setMouseTracking(False)

        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 设置占满屏幕
        self.resize(800, 600)
        # self.resize(screen.width(), screen.height())

    def updateTree(self):
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['name', 'path'])
        for dir in self.get_dir_list(AIR_PATH):
            print(dir)
            root = QTreeWidgetItem(self.tree)
            root.setText(0, dir)
            root.setText(1, '0')
            for file in self.get_file_list(os.path.join(AIR_PATH, dir)):
                child1 = QTreeWidgetItem(root)
                child1.setText(0, os.path.basename(file))
                child1.setText(1, file)

    def onTreeClicked(self, index):
        item = self.tree.currentItem()
        print(index.row())
        self.msg.emit(str(item.text(1)))
        # print('key=%s,value=%s' % (item.text(0), item.text(1)))

    def graphUI(self):
        layout = QVBoxLayout()

        layout_top = QHBoxLayout()
        button1 = QPushButton()
        button1.setText('312')
        button2 = QPushButton()
        button2.setText('456')

        layout_top.addWidget(button1, 1, Qt.AlignLeft | Qt.AlignTop)
        layout_top.addWidget(button2, 2, Qt.AlignLeft | Qt.AlignTop)

        layout_bottom = QHBoxLayout()
        layout_bottom.addWidget(self.tree)
        doc = fitz.open(r'G:\项目\efb\00026CHPPR.PDF')
        page = doc.loadPage(0)
        cover = self.render_pdf_page(page, True)

        self.label = QLabel()
        self.label.setScaledContents(True)
        self.label.setPixmap(QPixmap(cover))
        layout_bottom.addWidget(self.label)

        layout_bottom.setStretchFactor(self.label, 3)
        layout_bottom.setStretchFactor(self.tree, 1)
        layout.addLayout(layout_top)
        layout.addLayout(layout_bottom)
        self.tab1.setLayout(layout)

    def test(self):
        import time
        time.sleep(100)

    def checkListUI(self):
        btn_left = QPushButton()
        btn_left.setText('<')
        btn_left.clicked.connect(lambda: self.btn_Left(self.CheckView))
        btn_right = QPushButton()
        btn_right.setText('>')
        btn_right.clicked.connect(lambda: self.btn_Right(self.CheckView))
        self.CheckView.graphicsScene = QGraphicsScene()
        self.CheckView.pixmap = QPixmap(self.get_file_list(CHECK_PATH)[0])   #
        self.CheckView.pixmapItem = QGraphicsPixmapItem(self.CheckView.pixmap)
        self.CheckView.displayedImageSize = QSize(0, 0)
        self.CheckView.resize(600, 800)
        self.CheckView.graphicsScene.addItem(self.CheckView.pixmapItem)
        self.CheckView.setScene(self.CheckView .graphicsScene)
        layout = QHBoxLayout()
        layout.addWidget(btn_left)
        layout.addWidget(self.CheckView)
        layout.addWidget(btn_right)
        self.checkList.setLayout(layout)

    def btn_Left(self, view):
        clist = self.get_file_list(CHECK_PATH)
        self.ccount -= 1
        view.pixmap = QPixmap(clist[self.ccount % len(clist)])
        view.pixmapItem = QGraphicsPixmapItem(view.pixmap)
        view.graphicsScene.addItem(view.pixmapItem)
        view.setScene(view.graphicsScene)

    def btn_Right(self, view):
        clist = self.get_file_list(CHECK_PATH)
        self.ccount += 1
        view.pixmap = QPixmap(clist[self.ccount % len(clist)])
        view.pixmapItem = QGraphicsPixmapItem(view.pixmap)
        view.graphicsScene.addItem(view.pixmapItem)
        view.setScene(view.graphicsScene)

    # 获取所有文件名（递归）
    def get_file_list(self, path):
        l = list()
        if os.path.exists:
            for root, dirs, files in os.walk(path):
                for file in files:
                    l.append(os.path.join(root, file))
        return l

    # 获取一级目录下文件夹
    def get_dir_list(self, path):
        l = list()
        if os.path.exists:
            for dir in os.listdir(path):
                if os.path.isdir(os.path.join(AIR_PATH, dir)):
                    l.append(dir)
        return l



    # 显示 PDF 封面
    # page_data 为 page 对象
    def render_pdf_page(self, page_data, for_cover=False):
        # 图像缩放比例
        zoom_matrix = fitz.Matrix(4, 4)
        if for_cover:
            zoom_matrix = fitz.Matrix(1, 1).prerotate(int(90))

        # 获取封面对应的 Pixmap 对象
        # alpha 设置背景为白色
        pagePixmap = page_data.getPixmap(
            matrix=zoom_matrix,
            alpha=False)
        # 获取 image 格式
        imageFormat = QImage.Format_RGB888
        # 生成 QImage 对象
        pageQImage = QImage(
            pagePixmap.samples,
            pagePixmap.width,
            pagePixmap.height,
            pagePixmap.stride,
            imageFormat)
        # 生成 pixmap 对象
        pixmap = QPixmap()
        pixmap.convertFromImage(pageQImage)
        return pixmap


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = EfbMain()
    main.show()
    sys.exit(app.exec_())