#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os, re, time, zipfile, HTMLParser, itertools, tempfile
import StringIO, Image
import shutil
from PyQt4 import QtCore, QtGui, uic
from carnetPage import *


class AlWgt(QtGui.QTableWidgetItem):
	def __init__(self,p,t):
		QtGui.QTableWidgetItem.__init__(self,t)
		self.alObject = p
		self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)


class AlItem(object):
	def __init__(self,al,ft):
		self.alumne = al
		self.foto = ft
  
  
	def insert(self,t):
		t.insertRow(0)
		t.setItem(0, 0, AlWgt(self,QtCore.QString.fromUtf8(self.alumne)))




class Parser(HTMLParser.HTMLParser):
	def __init__(self):
		HTMLParser.HTMLParser.__init__(self)
		self.Data = []
		self.intag = 0
		
	def handle_starttag(self, tag, attrs):
		if tag == 'td' and attrs[0][1] == 'td_PrincipalAlu':
			self.intag = 1
	
	def handle_endtag(self,tag):
		if tag == 'td':
			if self.intag == 2:
				d = self.Data[-1].split()
				self.Data[-1] = ' '.join(d)
				
			self.intag = 0
	
	def handle_data(self,data):
		if self.intag:
			data = data.replace('\t','').replace('\n','')
			if self.intag == 1:
				self.Data.append(data)
				self.intag = 2
			elif self.intag == 2:
				self.Data[-1] += data
		
			
	
	def fileFeed(self, f):
		f = open(f)
		self.feed(''.join(f.readlines()))
		f.close()




def processPhoto(fn):
	im = Image.open(fn)
	if im.size[0] > 300:
		print "Massa grossa!"
		wpercent = (130/float(im.size[0]))
		hsize = int((float(im.size[1])*float(wpercent)))
		im = im.resize((130,hsize))
	
	buf = StringIO.StringIO()
	im.save(buf, format= 'JPEG')
	return buf.getvalue()



class PBarDlg(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("pbar.ui",self)


class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self,parent)
		self.ui = uic.loadUi("mainwindow.ui",self)
		
		self.ui.llistaAlumnes.horizontalHeader().setStretchLastSection(True)
		
		self.setWindowTitle("Carnets")
		self.connect(self.ui.actionCarrega,
			QtCore.SIGNAL("triggered()"), self.loadFile)
		self.connect(self.ui.actionFes_carnets,
			QtCore.SIGNAL("triggered()"), self.doCarnets)
		self.connect(self.ui.actionSurt,
			QtCore.SIGNAL("triggered()"),self.doExit)	
	
		self.connect(self.ui.llistaAlumnes,
			QtCore.SIGNAL("cellClicked(int,int)"), self.showAlumne)
		self.connect(self.ui.botFoto,
			QtCore.SIGNAL("clicked()"), self.canviarFoto)
		
		self.center()

		self.scene = QtGui.QGraphicsScene()
		self.ui.graphicsView.setScene(self.scene)
		self.selected = -1
		self.zip_file = None


	def doExit(self):
		self.close()

	def canviarFoto(self):
		if self.selected == -1:
			QtGui.QMessageBox.critical(self, "Alerta!", "Tria un alumne",
                QtGui.QMessageBox.Ok)
			return
		
		fn = QtGui.QFileDialog.getOpenFileName(self, "Load File")
		if fn == '': return
		
		data = processPhoto(str(fn))
		
		localFN = self.ui.llistaAlumnes.item(self.selected,0).alObject.foto
		
		zipf = zipfile.ZipFile(self.zip_file,"a")
		zipf.writestr(str(localFN),data)
		zipf.close()

		self.showAlumne(self.selected,0)


	def showAlumne(self,a,b):
		fn = self.ui.llistaAlumnes.item(a,0).alObject.foto
		q = QtGui.QPixmap()
		self.selected = a
		
		try:
			zipf = zipfile.ZipFile(self.zip_file,"r")
			data = zipf.read(str(fn))
			zipf.close()
			
			q.loadFromData(data)
			self.scene.clear()
			self.scene.addPixmap(q)
			self.ui.graphicsView.show()
		except:
			self.scene.clear()

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
		directory = os.path.dirname(str(fn))
		self.zip_file = directory + "/fotos.zip"
		try:
			zipf = zipfile.ZipFile(self.zip_file,"r")
		except:
			zipf = zipfile.ZipFile(self.zip_file,"w")
			# Hem d'escriure una entrada almanco dins el zip
			zipf.writestr("dummy","dummy")
		zipf.close()
		
		self.clearItems()
		
		p = Parser()
		p.fileFeed(fn)
		
		for data in p.Data:
			m = re.findall('.*-(.*)\((\d+)\)$', data)
			alName = m[0][0]
			exp = m[0][1]
			
			filename = exp + ".jpg"
			
			al = AlItem(alName, filename)
			al.insert(self.ui.llistaAlumnes)
	
	
	def doCarnets(self):
		nalumnes = self.ui.llistaAlumnes.rowCount()
		if nalumnes == 0:
			QtGui.QMessageBox.critical(self, "Alerta!", "No hi ha alumnes",
                QtGui.QMessageBox.Ok)
			return
		
		pBar = PBarDlg(self)
		pBar.show()
		
		tempDir = tempfile.mkdtemp()
		
		cp = CarnetPage()
		cp.loadTemplate()
		zipf = zipfile.ZipFile(self.zip_file,"r")
		nalumnes = self.ui.llistaAlumnes.rowCount()
		for i in range(0,nalumnes):
			al = self.ui.llistaAlumnes.item(i,0).alObject
			
			fotoFile = tempDir + "/" + al.foto
			
			try:
				data = zipf.read(al.foto)
				f = open(fotoFile,"w")
				f.write(data)
				f.close()
			except:
				os.system("cp nobody.jpg " + fotoFile)
				print al.alumne, "No te foto"			
			
			cp.newData(al.alumne, fotoFile)
			pBar.ui.progressBar.setValue(int(100.0*i/(nalumnes-1)))
			QtGui.QApplication.processEvents()
		
		cp.cleanup()
		zipf.close()
		
		print tempDir
		shutil.rmtree(tempDir)
		
		pBar.close()



if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	app.exec_()