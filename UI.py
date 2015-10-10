#!/usr/bin/python3

#  UI.py
#
#  Copyright (C) 2015 Caian Benedicto <caianbene@gmail.com>
#
#  This file is part of Asparagus
#
#  Asparagus is free software; you can redistribute it and/or modify it 
#  under the terms of the GNU General Public License as published by 
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  Asparagus is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

import sys, math, datetime
import Shapes, Expressions
from PyQt4 import QtGui, QtCore

app = None

def init():
    global app
    app = QtGui.QApplication(sys.argv)
    printer = MainWindow()
    return printer

def run():
    global app
    return app.exec_()

class CartesianView(QtGui.QGraphicsView):
    def __init__(self, parent = None):
        super(CartesianView, self).__init__(parent)
        self.scale(1, -1)

class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.dynscene = { }
    
    def initUI(self):
        self.scene = QtGui.QGraphicsScene(self)
        drawv = CartesianView(self)
        drawv.setScene(self.scene)
        drawv.setRenderHint(QtGui.QPainter.Antialiasing)
        drawv.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        drawv.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.addDefaultElements()
        #listv = QtGui.QListView(self)
        #split = QtGui.QSplitter(self)
        #split.addWidget(listv)
        #split.addWidget(drawv)
        #split.setStretchFactor(1, 4)
        vbox = QtGui.QVBoxLayout(self)
        #vbox.addWidget(split)
        vbox.addWidget(drawv)
        self.setLayout(vbox)
        self.setGeometry(300, 150, 1280, 720)
        self.setWindowTitle('Asparagus')
        self.show()

    def addDefaultElements(self):
        pass
        #expr = Expressions.ExpressionItem(0, 0)
        #self.scene.addItem(expr)

    ###############################
    # printer interface
    ###############################

    def print_object(self, name, pos, shape, alias, prop):
        t = shape['type']
        offx = shape.get('offx', 0)
        offy = shape.get('offy', 0)
        a = shape.get('angle', 0)
        if t == 'box':
            w = shape['width']
            h = shape['height']
            o = Shapes.Box(pos[0], pos[1], w, h, a, alias, offx, offy)
        elif t == 'ball':
            w = h = shape['radius'] * 2
            o = Shapes.Ball(pos[0], pos[1], w, h, a, alias, offx, offy)
        elif t == 'wall':
            w = shape['width']
            h = shape['height']
            l = shape.get('length', 20)
            i = shape.get('inclination', 135)
            d = shape.get('striped', 25)
            d0 = (math.sqrt(w**2+h**2) % d) / 2
            x0 = pos[0] - w / 2
            y0 = pos[1] - h / 2
            x1 = pos[0] + w / 2
            y1 = pos[1] + h / 2
            o = Shapes.Wall(x0, y0, x1, y1, i, l, d0, d)
        else:
            raise Exception('unknown object type %s' % t)
        self.scene.addItem(o)
        self.dynscene[name] = o

    def print_dynamic(self, name, dyn, pos, alias, prop):
        def assert_pos(name, n):
            if len(pos) != n:
                raise Exception('%s dynamic expects %d offsets, provided %d' % (name, n, len(pos)))
        if dyn == 'force':
            assert_pos('force', 4)
            d = Shapes.Arrow(pos[0], pos[1], pos[2], pos[3], alias)
        elif dyn == 'weight':
            assert_pos('weight', 4)
            d = Shapes.Arrow(pos[0], pos[1], pos[2], pos[3], alias)
        elif dyn == 'rod':
            assert_pos('rod', 4)
            d = Shapes.Rod(pos[0], pos[1], pos[2], pos[3], alias)
        elif dyn == 'spring':
            assert_pos('spring', 4)
            d = Shapes.Spring(pos[0], pos[1], pos[2], pos[3], alias)
        elif dyn == 'dampener':
            assert_pos('dampener', 4)
            d = Shapes.Dampener(pos[0], pos[1], pos[2], pos[3], alias)
        else:
            raise Exception('unknown dynamic type %s' % dyn)
        self.dynscene[name] = d
        self.scene.addItem(d)

    def print_angle(self, name, title):
        a = Shapes.ThetaPairDisplay(self.dynscene[name], title)
        self.scene.addItem(a)

    def print_diagnostic(self, level, message):
        print('[%s] (%d) %s' % (str(datetime.datetime.now()), level, message))

#class Example(QtGui.QWidget):
    
#    def __init__(self):
#        super(Example, self).__init__()
#        self.scene = None
#        self.view = None
#        self.initUI()
        
#    def initUI(self):
#        grid = QtGui.QGridLayout()
#        self.setLayout(grid)
#        self.scene = QtGui.QGraphicsScene(self)
#        self.view = QtGui.QGraphicsView(self.scene, self)
#        self.coolStuff();
#        grid.addWidget(self.view)
#        self.move(300, 150)
#        self.resize(1280, 720)
#        self.setWindowTitle('Asparagus')
#        self.show()

#    def coolStuff(self):
#        pen = QtGui.QPen()
#        pen.setColor(QtGui.QColor.fromRgb(0))
#        pen.setWidthF(4.0)
#        pen.setCapStyle(QtCore.Qt.RoundCap)
#        pen.setJoinStyle(QtCore.Qt.RoundJoin)

#        ellipse = QtGui.QGraphicsEllipseItem(-200, -100, 400, 200)
#        ellipse.setPen(pen)
#        self.scene.addItem(ellipse)

#        rectangle = QtGui.QGraphicsRectItem(-200, -100, 400, 200)
#        rectangle.setPen(pen)
#        self.scene.addItem(rectangle)