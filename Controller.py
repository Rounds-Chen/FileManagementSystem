from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction,QTableWidgetItem
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

from FCB import DIR, TXTFILE
from VirtualDisk import Disk
import shelve,os,re
from icos import *

class Ctrl(object):
    def __init__(self,ui):
        self._ui=ui
        self._disk=Disk(1024,1)
        self.initDisk()
        self._ui._parentFcb=self._disk._root
        self._ui._fcbs=self._disk._root._addr


    def initDisk(self):
        if not os.path.exists('test_shelf.db.dir'):
            return
        s=shelve.open('test_shelf.db')
        self._disk._fcbNums=s['fcbNums']
        self._disk._remainer=s['remainer']
        self._disk._bitmap=s['bitmap']
        self._disk._memory=s['memory']
        self._disk._root=s['fcb']


    # 检查当前目录下是否有重名文件
    def validateFileName(self,fileName,type,id):
        dupNum=0
        nameList=[]
        for f in self._ui._fcbs:
            if f._id!=id and f._type==type:
                nameList.append(f._filename)
        for name in nameList:
            if name.startswith(fileName):
                dupNum+=1
        if dupNum!=0:
            while fileName+'('+str(dupNum)+')' in nameList:
                dupNum+=1
            return fileName+'('+str(dupNum)+')'
        return fileName

    # 创建新文件夹
    def createDir(self):
        fcb=self._disk.mkdir(self._ui._parentFcb)
        fcb._filename=self.validateFileName(fcb._filename,DIR,fcb._id)
        self._ui._fcbs.append(fcb)

        rowInfo=[fcb._filename,fcb._time,'文件夹','']
        curRow = self._ui.tableWidget.rowCount() + 1
        self._ui.tableWidget.setRowCount(curRow)

        item = QTableWidgetItem(rowInfo[0])
        item.setIcon(QIcon(':/icos/dir.ico'))
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self._ui.tableWidget.setItem(curRow - 1, 0, item)

        for i in range(1, 4):
            item = QTableWidgetItem(rowInfo[i])
            if i==3:
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self._ui.tableWidget.setItem(curRow - 1, i, item)
        return fcb._filename

    # 创建新文件
    def createFile(self):
        fcb=self._disk.newFile(self._ui._parentFcb)
        if fcb==[]:
            print('磁盘空间不足——新建文件失败！')
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning, 'Warning', '磁盘空间不足')
            msg_box.setWindowIcon(QIcon(':/icos/warn.ico'))
            msg_box.exec_()
        else:
            print('磁盘空间充足——新建文件成功！')
            fcb._filename=self.validateFileName(fcb._filename,TXTFILE,fcb._id)
            self._ui._fcbs.append(fcb)

            rowInfo = [fcb._filename+'.txt',fcb._time,'文本文档','0KB']
            curRow=self._ui.tableWidget.rowCount()+1
            self._ui.tableWidget.setRowCount(curRow)

            for i in range(0,4):
                item=QTableWidgetItem(rowInfo[i])
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                if i==0:
                    item.setIcon(QIcon(':/icos/file.ico'))
                if i==3:
                    item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self._ui.tableWidget.setItem(curRow-1, i, item)

    # 修改文件
    def modify(self,fileFcb,content):
        self._disk.modify(fileFcb,content)

    # 读取文件
    def readFile(self,fileFcb):
        return self._disk.readFile(fileFcb)

    # 删除文件
    def delFile(self,fileFcb):
        self._disk.rm(fileFcb)

    # 格式化磁盘
    def format(self):
        self._disk.format()
        self._ui._parentFcb = self._disk._root
        self._ui._fcbs = self._disk._root._addr





