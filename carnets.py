#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, time
from PyQt4 import QtCore, QtGui, uic


class AlWgt(QtGui.QTableWidgetItem):
	def __init__(self,p,t):
		QtGui.QTableWidgetItem.__init__(self,t)
		self.taskObject = p
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


class AlItem(object):
	def __init__(self,al,ft):
		self.alumne = al
		self.foto = ft
  
  
	def insert(self,t):
		t.insertRow(0)
		t.setItem(0, 0, AlWgt(self,QtCore.QString.fromUtf8(self.alumne)))
		t.setItem(0, 1, AlWgt(self,QtCore.QString.fromUtf8(self.foto)))





class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		
		self.ui.llistaAlumnes.horizontalHeader().setStretchLastSection(True)
		
		self.setWindowTitle("Carnets")
		self.connect(self.ui.actionCarrega,
			QtCore.SIGNAL("triggered()"), self.loadFile)
		self.connect(self.ui.llistaAlumnes,
			QtCore.SIGNAL("cellClicked(int,int)"), self.showAlumne)
		
		self.center()
		
		self.ui.llistaAlumnes.setColumnWidth(0,350)
		#self.ui.llistaAlumnes.setColumnWidth(1,150)
		
		self.llista = []
		self.scene = QtGui.QGraphicsScene()
		self.ui.graphicsView.setScene(self.scene)

	def showAlumne(self,a,b):
		fn = self.ui.llistaAlumnes.item(a,1).text()
		q = QtGui.QPixmap()
		fot = self.directory + "/" + fn
		q.load(fot)
		self.scene.clear()
		self.scene.addPixmap(q)

	def clearItems(self):
		while self.ui.llistaAlumnes.item(0,0):
			self.ui.llistaAlumnes.removeRow(0)


	def center(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)



	def loadFile(self):
		fn = QtGui.QFileDialog.getOpenFileName(self, "Load File")
		if fn == ' ': return
		print fn
		m = re.search('(.*)/(.*)',str(fn))
		self.directory = m.group(1)
		self.filename = fn
		
		self.clearItems()
		f = open(fn)
		for l in f:
			m = re.findall('^(.*?)\s\s+(.*)$',l)
			al = AlItem(m[0][0],m[0][1])
			al.insert(self.ui.llistaAlumnes)
		f.close()



if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()