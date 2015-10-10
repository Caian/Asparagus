#!/usr/bin/python3

#  Shapes.py
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

import math
from PyQt4 import QtGui, QtCore

def texToRTF(text):
    if text == None:
        return None
    rtf = ''
    sup = False
    sub = False
    bra = False
    def next(i):
        if i+1 < len(text):
            return text[i+1]
        else: 
            raise Exception('latex error')
    i = 0
    while i < len(text):
        c = text[i]
        if c == '^':
            rtf += '<sup>'
            sup = True
        elif c == '_':
            rtf += '<sub>'
            sub = True
        elif c == '{' or c == '}':
            raise Exception('latex error')
        else:
            rtf += c
            i += 1
            continue
        n = next(i)
        i += 1
        if n == '{':
            while True:
                b = next(j)
                i += 1
                if b == '}':
                    break
                elif b == '_' or b == '^' or b == '{':
                    raise Exception('latex nesting not allowed')
                rtf += b
        else:
            rtf += n
        if sup:
            rtf += '</sup>'
            sup = False
        elif sub:
            rtf += '</sub>'
            sub = False
        i += 1
    return ''.join(rtf)

def getDefaultForeColor():
    return QtGui.QColor('black')

def getDefaultBackColor():
    return QtGui.QColor('white')

def getDefaultHighlightColor():
    return QtGui.QColor.fromRgb(0x00c6de)

def getDefaultTickness():
    return 3.0

def getDefaultArrowTickness():
    return 3.0

def getDefaultArrowLength():
    return 50.0

def getDefaultArrowHeadWidth():
    return 20.0

def getDefaultArrowHeadHeight():
    return 20.0

def getDefaultSpringWidth():
    return 45.0

def getDefaultSpringHeight():
    return 20.0

def getDefaultDampenerWidth():
    return 15.0

def getDefaultDampenerHeight():
    return 25.0

def getDefaultAngularRefRadius():
    return 30.0

def getDefaultAngularRefLineLenAdd():
    return 30.0

def getDefaultAngularRefTickness():
    return 2.0

def getDefaultFontFamily():
    return 'Sans'

def getDefaultFontSize():
    return 24

def getDefaultFont():
    font = QtGui.QFont()
    font.setFamily('Sans')
    font.setPixelSize(24)
    return font

def getDefaultPen(highlighted = False):
    pen = QtGui.QPen()
    pen.setColor(getDefaultForeColor() if not highlighted else 
                 getDefaultHighlightColor())
    pen.setWidthF(getDefaultTickness())
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    return pen

def getDefaultForeBrush(highlighted = False):
    return (getDefaultForeColor() if not highlighted else 
            getDefaultHighlightColor())

def getDefaultBackBrush():
    return getDefaultBackColor()

class SceneItem(QtGui.QGraphicsObject):
    def __init__(self):
        super(SceneItem, self).__init__()
        self.highlighted = False

class PairPointItem(SceneItem):
    def __init__(self, x0, y0, x1, y1):
        super(PairPointItem, self).__init__()
        self.setX(x0)
        self.setY(y0)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

class SceneObjectItem(SceneItem):
    def __init__(self, x, y, angle, offx = 0, offy = 0):
        super(SceneObjectItem, self).__init__()
        self.setX(x)
        self.setY(y)
        self.angle = angle
        self.offx = offx
        self.offy = offy

class Box(SceneObjectItem):
    def __init__(self, x, y, width, height, angle, title, offx, offy):
        super(Box, self).__init__(x, y, angle, offx, offy)
        self.title = texToRTF(title)
        self.width = width
        self.height = height

    def boundingRect(self):
        hw = self.width / 2.0
        hh = self.height / 2.0
        return QtCore.QRectF(-hw-self.offx, -hh-self.offy, self.width, self.height)

    def paint(self, painter, option, widget):
        w = self.width
        h = self.height
        hw = w / 2.0
        hh = h / 2.0
        pen = getDefaultPen(self.highlighted)
        brush = getDefaultBackBrush()
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.rotate(self.angle)
        painter.translate(-self.offx, -self.offy)
        painter.drawRect(-hw, -hh, w, h)
        painter.rotate(-self.angle)
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Ball(SceneObjectItem):
    def __init__(self, x, y, width, height, angle, title, offx, offy):
        super(Ball, self).__init__(x, y, angle, offx, offy)
        self.title = texToRTF(title)
        self.width = width
        self.height = height

    def boundingRect(self):
        hw = self.width / 2.0
        hh = self.height / 2.0
        return QtCore.QRectF(-hw, -hh, self.width, self.height)

    def paint(self, painter, option, widget):
        w = self.width
        h = self.height
        hw = w / 2.0
        hh = h / 2.0
        pen = getDefaultPen(self.highlighted)
        brush = getDefaultBackBrush()
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.rotate(self.angle)
        painter.translate(-self.offx, -self.offy)
        painter.drawEllipse(-hw, -hh, w, h)
        painter.rotate(-self.angle)
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Arrow(PairPointItem):
    def __init__(self, x0, y0, x1, y1, title):
        super(Arrow, self).__init__(x0, y0, x1, y1)
        self.lineWidth = getDefaultArrowTickness()
        self.headWidth = getDefaultArrowHeadWidth()
        self.headHeight = getDefaultArrowHeadHeight()
        self.title = texToRTF(title)

    def boundingRect(self):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        return QtCore.QRectF(0, 0, dx, dy)

    def paint(self, painter, option, widget):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        hw = self.headWidth
        hh = self.headHeight
        angle = 180 * math.atan2(dy, dx) / math.pi
        length = math.sqrt((dx**2)+(dy**2))
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        brush = getDefaultForeBrush(self.highlighted)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.rotate(angle)
        painter.drawLine(0, 0, length-hw/2, 0)
        pen.setWidthF(1.0)
        painter.setPen(pen)
        painter.drawPolygon(
            QtCore.QPointF(length, 0.0),
            QtCore.QPointF(length-hw,-hh/2),
            QtCore.QPointF(length-hw, hh/2)
        )
        fontsz = getDefaultFontSize()
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        rd = max(sz.width(), sz.height()) / 2
        painter.translate(length, 5+rd)
        painter.rotate(-angle)
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Rod(PairPointItem):
    def __init__(self, x0, y0, x1, y1, title, showTraction = True):
        super(Rod, self).__init__(x0, y0, x1, y1)
        self.title = texToRTF(title)
        self.lineWidth = getDefaultTickness()

    def boundingRect(self):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        return QtCore.QRectF(0, 0, dx, dy)

    def paint(self, painter, option, widget):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        angle = 180 * math.atan2(dy, dx) / math.pi
        length = math.sqrt((dx**2)+(dy**2))
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        painter.rotate(angle)
        line = QtGui.QPolygonF()
        line.append(QtCore.QPointF(0.0, 0.0))
        line.append(QtCore.QPointF(length, 0.0))
        painter.drawPolyline(line)
        fontsz = getDefaultFontSize()
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        rd = max(sz.width(), sz.height()) / 2
        painter.translate(length/2, 5+rd)
        painter.rotate(-angle)
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Spring(PairPointItem):
    def __init__(self, x0, y0, x1, y1, title, headWidthAsRatio = True):
        super(Spring, self).__init__(x0, y0, x1, y1)
        self.title = texToRTF(title)
        self.lineWidth = getDefaultTickness()
        self.headWidthAsRatio = headWidthAsRatio
        if headWidthAsRatio:
            dx = self.x1 - self.x0
            dy = self.y1 - self.y0
            length = math.sqrt((dx**2)+(dy**2))
            self.springWidth = getDefaultSpringWidth() / length
        else:
            self.springWidth = getDefaultSpringWidth()
        self.springHeight = getDefaultSpringHeight()

    def boundingRect(self):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        return QtCore.QRectF(0, 0, dx, dy)

    def paint(self, painter, option, widget):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        angle = 180 * math.atan2(dy, dx) / math.pi
        length = math.sqrt((dx**2)+(dy**2))
        sw = self.springWidth
        sh = self.springHeight
        if self.headWidthAsRatio:
            sw = sw * length
        sx0 = (length-sw)/2.0
        sx1 = (length+sw)/2.0
        sy0 = -sh/2.0
        sy1 = sh/2.0
        n = 4
        dw = sw/n
        j = sh/2
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        painter.rotate(angle)
        line = QtGui.QPolygonF()
        line.append(QtCore.QPointF(0.0, 0.0))
        line.append(QtCore.QPointF(sx0, 0.0))
        for i in range(n):
            line.append(QtCore.QPointF(sx0 + dw/2 + dw*i, j))
            j *= -1
        line.append(QtCore.QPointF(sx1, 0.0))
        line.append(QtCore.QPointF(length, 0.0))
        painter.drawPolyline(line)
        fontsz = getDefaultFontSize()
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        rd = max(sz.width(), sz.height()) / 2
        painter.translate(length/2, sh+rd)
        painter.rotate(-angle)
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Dampener(PairPointItem):
    def __init__(self, x0, y0, x1, y1, title):
        super(Dampener, self).__init__(x0, y0, x1, y1)
        self.title = texToRTF(title)
        self.lineWidth = getDefaultTickness()
        self.dampenerWidth = getDefaultDampenerWidth()
        self.dampenerHeight = getDefaultDampenerHeight()

    def boundingRect(self):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        return QtCore.QRectF(0, 0, dx, dy)

    def paint(self, painter, option, widget):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        angle = 180 * math.atan2(dy, dx) / math.pi
        length = math.sqrt((dx**2)+(dy**2))
        dw = self.dampenerWidth
        dh = self.dampenerHeight
        dx0 = (length-dw)/2.0
        dx1 = (length+dw)/2.0
        dy0 = -dh/2.0
        dy1 = dh/2.0
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        brush = getDefaultForeBrush(self.highlighted)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.rotate(angle)
        painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(dx0, 0))
        painter.drawLine(QtCore.QPointF(dx1, 0), QtCore.QPointF(length, 0))
        painter.drawPolyline(
            QtCore.QPointF(dx1, dy0),
            QtCore.QPointF(dx0, dy0),
            QtCore.QPointF(dx0, dy1),
            QtCore.QPointF(dx1, dy1),
        )
        painter.drawRect(QtCore.QRectF(dx0 + 2*self.lineWidth, dy0 + 2*self.lineWidth, 
            dw - 2*self.lineWidth, dh - 4*self.lineWidth))
        fontsz = getDefaultFontSize()
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.title)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        rd = max(sz.width(), sz.height()) / 2
        painter.translate(length/2, dh+rd)
        painter.rotate(-angle)
        painter.translate(-sz.width()/2, sz.height()/2)
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(0, 0), text)

class Wall(PairPointItem):
    def __init__(self, x0, y0, x1, y1, a, w, d0, d):
        super(Wall, self).__init__(x0, y0, x1, y1)
        self.lineWidth = getDefaultTickness()
        self.stripeAngle = a
        self.stripeWidth = w
        self.stripeStart = d0
        self.stripeStep = d

    def boundingRect(self):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        return QtCore.QRectF(0, 0, dx, dy)

    def paint(self, painter, option, widget):
        dx = self.x1 - self.x0
        dy = self.y1 - self.y0
        angle = math.atan2(dy, dx)
        length = math.sqrt((dx**2)+(dy**2))
        a = self.stripeAngle
        w = self.stripeWidth
        d0 = self.stripeStart
        d = self.stripeStep
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(dx, dy))
        angle += a/180*math.pi
        dx /= length
        dy /= length
        i = d0
        while i <= length:
            x0 = dx * i
            y0 = dy * i
            x1 = x0 + math.cos(angle) * w
            y1 = y0 + math.sin(angle) * w
            painter.drawLine(QtCore.QPointF(x0, y0), QtCore.QPointF(x1, y1))
            i += d

class ThetaPairDisplay(SceneItem):
    def __init__(self, item, theta1, theta2 = None):
        super(ThetaPairDisplay, self).__init__()
        self.lineWidth = getDefaultAngularRefTickness()
        self.radius = getDefaultAngularRefRadius()
        self.bothSides = (theta2 != None)
        self.theta1 = texToRTF(theta1)
        self.theta2 = texToRTF(theta2)
        self.item = item

    def boundingRect(self):
        r = self.radius
        if self.bothSides:
            dx = self.item.x1 - self.item.x0
            dy = self.item.y1 - self.item.y0
            return QtCore.QRectF(-r, -r, dx+r, dy+r)
        else:
            return QtCore.QRectF(-r, -r, r, r)

    def paint(self, painter, option, widget):
        painter.translate(self.item.x0, self.item.y0)
        r = self.radius
        l = getDefaultAngularRefLineLenAdd()
        dx = self.item.x1 - self.item.x0
        dy = self.item.y1 - self.item.y0
        angle = math.atan2(dx, -dy)
        angle2 = math.atan2(-dx, dy)
        hangle = -math.pi/2 - angle/2
        hangle2 = math.pi/2 - angle - math.pi/4
        rect = QtCore.QRect(-r, -r, 2*r, 2*r)
        pen = getDefaultPen(self.highlighted)
        pen.setWidthF(self.lineWidth)
        painter.setPen(pen)
        painter.drawPie(rect, -16*(-90), -16*(180*angle/math.pi))
        painter.drawLine(0, -r, 0, -r-l)
        fontsz = getDefaultFontSize()
        font = getDefaultFont()
        painter.setFont(font)
        text = QtGui.QStaticText()
        text.setText(self.theta1)
        text.prepare(QtGui.QTransform(), font)
        sz = text.size()
        rd = max(sz.width(), sz.height()) / 2
        painter.scale(1, -1)
        painter.drawStaticText(QtCore.QPointF(-(r+rd)*math.cos(hangle)-sz.width()/2, 
            -(r+rd)*math.sin(hangle)-sz.height()/2), text)
        if self.bothSides:
            text = QtGui.QStaticText()
            text.setText(self.theta2)
            text.prepare(QtGui.QTransform(), font)
            sz = text.size()
            rd = max(sz.width(), sz.height()) / 2
            painter.scale(1, -1)
            painter.translate(dx, dy)
            painter.drawPie(rect, -16*(-90), -16*(180*angle2/math.pi))
            painter.drawLine(0, -r, 0, -r-l)
            painter.scale(1, -1)
            painter.drawStaticText(QtCore.QPointF(-(r+rd)*math.cos(hangle2)-sz.width()/2, 
                -(r+rd)*math.sin(hangle2)-sz.height()/2), text)