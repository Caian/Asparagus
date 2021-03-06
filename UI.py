﻿#!/usr/bin/python3

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
    tm = printer
    return printer, tm

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
        self.curreqns = []
        self.dynscene = { }
        self.refscene = { }
        self.timemachine = []
        self.tmi = -1

    def initUI(self):
        self.scene = QtGui.QGraphicsScene(self)
        drawv = CartesianView(self)
        drawv.setScene(self.scene)
        drawv.setRenderHint(QtGui.QPainter.Antialiasing)
        drawv.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        drawv.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        drawv.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.bpp = QtGui.QPushButton('<<')
        self.bpp.clicked.connect(self.tmPPrevious)
        self.bp = QtGui.QPushButton('<')
        self.bp.clicked.connect(self.tmPrevious)
        self.li = QtGui.QLabel('0/0')
        self.li.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        self.bn = QtGui.QPushButton('>')
        self.bn.clicked.connect(self.tmNext)
        self.bnn = QtGui.QPushButton('>>')
        self.bnn.clicked.connect(self.tmNNext)
        hbox0 = QtGui.QHBoxLayout(self)
        hbox0.addWidget(self.bpp)
        hbox0.addWidget(self.bp)
        hbox0.addWidget(self.li)
        hbox0.addWidget(self.bn)
        hbox0.addWidget(self.bnn)
        panel = QtGui.QFrame(self)
        panel.setLayout(hbox0)
        hbox1 = QtGui.QVBoxLayout(self)
        hbox1.addWidget(drawv)
        hbox1.addWidget(panel)
        frame = QtGui.QFrame(self)
        frame.setLayout(hbox1)
        self.addDefaultElements()
        self.console = QtGui.QListWidget(self)
        split = QtGui.QSplitter(self)
        split.setOrientation(QtCore.Qt.Vertical)
        split.addWidget(frame)
        split.addWidget(self.console)
        split.setSizes([720 - 720//4, 720//4])
        hbox2 = QtGui.QVBoxLayout(self)
        hbox2.addWidget(split)
        self.setLayout(hbox2)
        self.setGeometry(300, 150, 1280, 720)
        self.setWindowTitle('Asparagus')
        self.show()

    def addDefaultElements(self):
        pass

    ###############################
    # TimeMachine controls
    ###############################

    def tmPPrevious(self):
        last = self.tmi
        self.tmi = 0
        self.tmUpdate()
        self.tmDraw(last)

    def tmPrevious(self):
        last = self.tmi
        self.tmi -= 1
        self.tmUpdate()
        self.tmDraw(last)

    def tmNext(self):
        last = self.tmi
        self.tmi += 1
        self.tmUpdate()
        self.tmDraw(last)

    def tmNNext(self):
        last = self.tmi
        self.tmi = len(self.timemachine) - 1
        self.tmUpdate()
        self.tmDraw(last)

    def tmUpdate(self):
        l = len(self.timemachine)
        self.li.setText('%d/%d' % (self.tmi+1, l))
        self.bp.setEnabled(self.tmi > 0)
        self.bpp.setEnabled(self.tmi > 0)
        self.bn.setEnabled(self.tmi < l-1)
        self.bnn.setEnabled(self.tmi < l-1)

    ###############################
    # TimeMachine interface
    ###############################

    def clear_tm(self):
        self.timemachine = []
        self.tmUpdate()

    def add_highlight_eqn(self, obj, dyn, eqns):
        if len(eqns) == 0:
            return
        obj = self.dynscene[obj['$.name']] if obj != None else None
        dyn = self.dynscene[dyn.name] if dyn != None else None
        eqns = [str(s) for s in eqns]
        self.timemachine.append(('hl3', obj, dyn, eqns))
        self.tmUpdate()

    def add_rf(self, obj, nt, nr, at, dr, titles):
        obj = self.dynscene[obj['$.name']]
        self.timemachine.append(('ref', obj, nt, nr, at, dr, titles))
        self.tmUpdate()

    ###############################
    # TimeMachine rendering
    ###############################

    def tmDraw(self, last):
        
        # Undo last step
        if last >= 0:
            ti = self.timemachine[last]
            if ti[0] == 'hl3':
                # Remove the highlights
                if ti[1] != None:
                    ti[1].highlighted = False
                if ti[2] != None:
                    ti[2].highlighted = False
                # Remove previous eqn box
                if self.curreqns != None:
                    self.scene.removeItem(self.curreqns)
                self.curreqns = None
            elif ti[0] == 'ref':
                if ti[1] != None:
                    ti[1].highlighted = False

        # Roll back reference frames ahead of tmi
        l = []
        for i,r in self.refscene.items():
            if i >= self.tmi:
                self.scene.removeItem(r)
                l.append(i)
            else:
                r.highlighted = False
        for i in l:
            self.refscene.pop(i)

        # Add reference frames before tmi
        for i in range(last+1, self.tmi):
            ti = self.timemachine[i]
            if ti[0] == 'ref':
                ref = Shapes.RefFrame(ti[1], ti[2], ti[3], ti[4], ti[5], ti[6])
                self.scene.addItem(ref)
                self.refscene[i] = ref

        if self.tmi >= 0:
            ti = self.timemachine[self.tmi]
            if ti[0] == 'hl3':
                b = None
                # Highlight objects and compute a good place to put the eqn box
                if ti[1] != None:
                    ti[1].highlighted = True
                    b = ti[1].boundingRect().translated(ti[1].x(), ti[1].y())
                if ti[2] != None:
                    ti[2].highlighted = True
                    if b == None:
                        b = ti[2].boundingRect().translated(ti[2].x(), ti[2].y())
                    else:
                        b = b.united(ti[2].boundingRect().translated(ti[2].x(), ti[2].y()))
                # Add eqn box
                eqns = [Expressions.SymbolElement(e) for e in ti[3]]
                self.curreqns = Expressions.ExpressionList(0, 0, eqns)
                if b != None:
                    c = self.curreqns.boundingRect()
                    x = b.right() + 10
                    y = b.center().y() + c.height()/2
                else:
                    b = None
                    for n, i in self.dynscene.items():
                        if b == None:
                            c = i.boundingRect()
                            b = c.translated(i.x(), i.y())
                        else:
                            c = i.boundingRect()
                            c.translate(i.x(), i.y())
                            b = b.united(c)
                    r = b.center()
                    c = self.curreqns.boundingRect()
                    x = r.x() - c.width()/2
                    y = r.y() + c.height()/2
                self.curreqns.setX(x)
                self.curreqns.setY(y)
                self.scene.addItem(self.curreqns)
            elif ti[0] == 'ref':
                if ti[1] != None:
                    ti[1].highlighted = True
                # Add Ref Frames
                ref = Shapes.RefFrame(ti[1], ti[2], ti[3], ti[4], ti[5], ti[6])
                ref.highlighted = True
                self.scene.addItem(ref)
                self.refscene[self.tmi] = ref

        # Re-render the entire scene to avoid bugs with
        # partially updated areas
        self.scene.update()

    ###############################
    # printer interface
    ###############################

    def print_object(self, name, pos, shape, alias, prop):
        t = shape['type']
        offx = shape.get('offx', 0)
        offy = shape.get('offy', 0)
        rfox = shape.get('rfox', None)
        rfoy = shape.get('rfoy', None)
        a = shape.get('angle', 0)
        if t == 'box':
            w = shape['width']
            h = shape['height']
            o = Shapes.Box(pos[0], pos[1], w, h, a, 
                    alias, offx, offy, rfox, rfoy)
        elif t == 'ball':
            w = h = shape['radius'] * 2
            o = Shapes.Ball(pos[0], pos[1], w, h, a, 
                    alias, offx, offy, rfox, rfoy)
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
        elif dyn == 'torque':
            assert_pos('torque', 2)
            r = float(prop.get('radius', Shapes.getDefaultCArrowRadius()))
            c = prop.get('ccw', '0')
            if c == '0':
                c = False
            else:
                c = True
            d = Shapes.CircularArrow(pos[0], pos[1], r, alias)
        elif dyn == 'belt':
            assert_pos('belt', 4)
            c = prop.get('crossed', '0')
            r0 = float(prop['r0'])
            r1 = float(prop['r1'])
            if c == '0':
                c = False
            else:
                c = True
            d = Shapes.Belt(pos[0], pos[1], r0, pos[2], pos[3], r1, c, alias)
        elif dyn == 'angularspring':
            assert_pos('angularspring', 2)
            r = float(prop.get('radius', Shapes.getDefaultCArrowRadius()))
            d = Shapes.AngularSpring(pos[0], pos[1], r, alias)
        elif dyn == 'angulardampener':
            assert_pos('angulardampener', 2)
            r = float(prop.get('radius', Shapes.getDefaultCArrowRadius()))
            d = Shapes.AngularDampener(pos[0], pos[1], r, alias)
        else:
            raise Exception('unknown dynamic type %s' % dyn)
        self.dynscene[name] = d
        self.scene.addItem(d)

    def print_angle(self, name, title):
        a = Shapes.ThetaPairDisplay(self.dynscene[name], title)
        self.scene.addItem(a)

    def print_diagnostic(self, level, message):
        s = '[%s] (%d) %s' % (str(datetime.datetime.now()), level, message)
        i = QtGui.QListWidgetItem(s)
        b1 = QtGui.QColor.fromRgb(255, 90, 90)
        self.console.addItem(i)
        i.setSelected(True)
        if level < 3:
            i.setBackgroundColor(b1)
        self.console.scrollToBottom()
        print(s)

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