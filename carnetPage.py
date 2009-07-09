# -*- coding: utf-8 -*-
import uno,re, os
from com.sun.star.beans import PropertyValue
import ooutils


class CarnetPage(object):
	fname = "/tmp/pg%d"
	
	def __init__(self):
		self.counter = 0
		self.oor = ooutils.OORunner()
		self.desktop = self.oor.connect()
	
	def loadTemplate(self):
		self.model = self.desktop.loadComponentFromURL("file://" + os.getcwd() + "/carnets.ott" ,"_blank", 0, ())
		frames = self.model.getTextFrames()
		self.nms = [frames.n1,frames.n2,frames.n3,frames.n4,frames.n5,frames.n6,frames.n7,frames.n8,frames.n9]
		self.fts = [frames.f1,frames.f2,frames.f3,frames.f4,frames.f5,frames.f6,frames.f7,frames.f8,frames.f9]
		
	def newData(self,nm,ft):
		if len(self.nms) == 0:
			self.cleanup()
			self.loadTemplate()
		
		n = self.nms.pop(0)
		f = self.fts.pop(0)
		n.setString(nm)
		t = f.Text
		cursor = t.createTextCursor()
		graphic = self.model.createInstance( "com.sun.star.text.TextGraphicObject" ) 
		t.insertTextContent(cursor, graphic, False )
		dr = os.getcwd()
		graphic.GraphicURL = "file://" + dr + "/data/" + ft
		h = graphic.Height
		fact = float(f.Width)/float(graphic.Width)
		graphic.Width = f.Width
		graphic.Height = h*fact
	
	def cleanup(self):
		fn = CarnetPage.fname % (self.counter)
		self.model.storeAsURL("file://" + fn + ".odt", ())
		
		property = (PropertyValue( "FilterName" , 0, "writer_pdf_Export" , 0 ),)
		self.model.storeToURL("file://" + fn + ".pdf", property)		
		
		self.model.dispose()
		self.counter += 1





#cp = CarnetPage()
#cp.loadTemplate()
#f = open("data/data.txt")
#for l in f:
	#d = re.findall('^(.*?)\s\s+(.*)$',l)
	#cp.newData(d[0][0],d[0][1])
	#print ".",
#f.close()
#cp.cleanup()
