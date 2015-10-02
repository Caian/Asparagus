#!/usr/bin/python3
# -*- coding: utf8 -*-

#  Expressions.py
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
import Shapes
from PyQt4 import QtGui, QtCore

def getDefaultExpressionPen():
    pen = Shapes.getDefaultPen()
    pen.setWidthF(1.0)
    return pen

class ExpressionItem(Shapes.SceneItem):
    def __init__(self, x, y):
        super(ExpressionItem, self).__init__()
        self.setX(x)
        self.setY(y)
        self.tree = []
        self.tree.append(DerivativeElement('ttt',[ParenthesisElement(DivisionElement(ParenthesisElement(SymbolElement("TxbaconcymcebolaT")),
            ParenthesisElement(DivisionElement(
            SymbolElement("d<sup>2</sup>"), 
            SymbolElement("dt<sup>2</sup>"))))), SymbolElement('foo'), SymbolElement('bar'), DivisionElement(
            SymbolElement("d<sup>2</sup>"), 
            SymbolElement("dt<sup>2</sup>"))]))

    def boundingRect(self):
        return QtCore.QRectF(0, 0, 0, 0)

    def paint(self, painter, option, widget):
        pen = getDefaultExpressionPen()
        font = Shapes.getDefaultFont()
        brush = Shapes.getDefaultForeBrush()
        pen.setWidthF(2.0)
        painter.scale(1, -1)
        painter.setPen(pen)
        painter.setFont(font)
        painter.setBrush(brush)
        for i in self.tree:
            i.paint(painter, font, 0, 0);

class SymbolElement():
    def __init__(self, symbol):
        self.text = QtGui.QStaticText()
        self.text.setText(Shapes.texToRTF(symbol))

    def boundingRect(self, font):
        self.text.prepare(QtGui.QTransform(), font)
        sz = self.text.size()
        w = sz.width()
        h = sz.height()
        hw = w / 2.0
        hh = h / 2.0
        return QtCore.QRectF(-hw, -hh, w, h)

    def paint(self, painter, font, x, y):
        self.text.prepare(QtGui.QTransform(), font)
        sz = self.text.size()
        xt = x - sz.width() / 2;
        yt = y - sz.height() / 2;
        painter.drawStaticText(QtCore.QPointF(xt, yt), self.text)

class DivisionElement():
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def boundingRect(self, font):
        r1 = self.top.boundingRect(font)
        r2 = self.bottom.boundingRect(font)
        w = max(r1.width(), r2.width())
        h = r1.height() + r2.height() + 6
        l = -w / 2.0
        hh = h / 2.0
        t = r1.top()-r1.height()/2 - 6
        return QtCore.QRectF(l, t, w, h)

    def paint(self, painter, font, x, y):
        r1 = self.top.boundingRect(font)
        r2 = self.bottom.boundingRect(font)
        y1 = y - r1.height() / 2 - 2
        self.top.paint(painter, font, x, y1)
        y2 = y + r2.height() / 2 + 4
        self.bottom.paint(painter, font, x, y2)
        l = min(r1.left(), r2.left()) + x
        r = max(r1.right(), r2.right()) + x
        painter.drawLine(l, y, r, y)

class LParElement():
    def __init__(self):
        self.rhf = 1.2
        self.rwd = 1.7
        self.rwf = 0.3
        self.ra = 120
        self.rb = 120
        self.rc = 10
        self.axf = 0.07
        self.ayf = 0.1
        self.awf = 1.1
        self.ahf = (self.rhf-1)/2 + self.rhf

    def boundingRect(self, h0):
        h = 1.09 * h0
        w = 1.2 * h0 / 1.7 / 2
        a = 120
        b = 120
        c = 10
        x0 = -0.3*(1.2 * h0 / 1.7)
        y0 = -h0/2 - 0.045*h0
        w *= 0.6
        return QtCore.QRectF(x0, y0, w, h)

    def paint(self, painter, font, x, y, h0):
        h = 1.2 * h0
        w = h / 1.7
        a = 120
        b = 120
        c = 10
        x0 = x - 0.3*w
        y0 = y - h0/2 - 0.1*h0
        path = QtGui.QPainterPath()
        path.arcMoveTo(x0, y0, w, h, a)
        path.arcTo(x0, y0, w, h, a, b)
        path.arcTo(x0+0.07*w/2, y0-0.1*h/2, 1.1*w, 1.1*h, a+b-c, -b+2*c)
        path.closeSubpath()
        painter.drawPath(path);

class RParElement():
    def __init__(self):
        self.rhf = 1.2
        self.rwd = 1.7
        self.rwf = 0.3
        self.ra = 120
        self.rb = 120
        self.rc = 10
        self.axf = 0.07
        self.ayf = 0.1
        self.awf = 1.1
        self.ahf = (self.rhf-1)/2 + self.rhf

    def boundingRect(self, h0):
        h = 1.09 * h0
        w = 0.66 * 1.1 * h0 / 1.7 / 2
        a = 120
        b = 120
        c = 10
        x0 = 0
        y0 = -h0/2 - 0.045*h0
        return QtCore.QRectF(x0, y0, w, h)

    def paint(self, painter, font, x, y, h0):
        h = 1.2 * h0
        w = h / 1.7
        a = -60
        b = 120
        c = 10
        x0 = x - 0.7*w
        y0 = y - h0/2 - 0.1*h0
        path = QtGui.QPainterPath()
        path.arcMoveTo(x0, y0, w, h, a)
        path.arcTo(x0, y0, w, h, a, b)
        path.arcTo(x0-0.27*w/2, y0-0.1*h/2, 1.1*w, 1.1*h, a+b-c, -b+2*c)
        path.closeSubpath()
        painter.drawPath(path);

class ParenthesisElement():
    def __init__(self, content):
        self.content = content
        self.lpar = LParElement()
        self.rpar = RParElement()

    def boundingRect(self, font):
        r = self.content.boundingRect(font)
        w = r.width()
        h = r.height()
        lr = self.lpar.boundingRect(h)
        rr = self.rpar.boundingRect(h)
        h = max(lr.height(), rr.height())
        t = r.center().y() - h/2
        l = r.left() - lr.width()
        w += lr.width() + rr.width()
        return QtCore.QRectF(l, t, w, h)

    def paint(self, painter, font, x, y):
        r = self.content.boundingRect(font)
        r.translate(x, y)
        self.content.paint(painter, font, x, y)
        self.lpar.paint(painter, font, r.left(), r.center().y(), r.height())
        self.rpar.paint(painter, font, r.right(), r.center().y(), r.height())

class OperatorElement():
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = args

    def boundingRect(self, font):
        r = self.symbol.boundingRect(font)
        h = r.height()
        w = r.width() * (len(self.args) - 1)
        for arg in self.args:
            r = arg.boundingRect(font)
            w += r.width()
            h = max(h, r.height())
        hh = h / 2
        return QtCore.QRectF(0, -hh, w, h)

    def paint(self, painter, font, x, y):
        rs = self.symbol.boundingRect(font)
        ra = [arg.boundingRect(font) for arg in self.args]
        dy = max([rs.bottom() + rs.top()] + [r.bottom() + r.top() for r in ra], key=abs)
        dy = dy / 2
        x -= ra[0].left()
        self.args[0].paint(painter, font, x, y - dy)
        x += ra[0].width() / 2
        for arg, r in zip(self.args[1:], ra[1:]):
            x -= rs.left()
            self.symbol.paint(painter, font, x, y - dy)
            x += rs.width() / 2
            x -= r.left()
            arg.paint(painter, font, x, y - dy)
            x += r.width() / 2

class FunctionElement():
    def __init__(self, symbol, args):
        self.symbol = symbol
        self.args = ParenthesisElement(OperatorElement(SymbolElement(' , '), args))

    def boundingRect(self, font):
        rs = self.symbol.boundingRect(font)
        ra = self.args.boundingRect(font)
        w = rs.width() + ra.width()
        h = max(rs.height(), ra.height())
        hw = w / 2
        hh = h / 2
        return QtCore.QRectF(hh, hw, w, h)

    def paint(self, painter, font, x, y):
        rs = self.symbol.boundingRect(font)
        ra = self.args.boundingRect(font)
        w = rs.width() + ra.width()
        h = max(rs.height(), ra.height())
        hw = w / 2
        hh = h / 2
        x0 = x - (hw + rs.left())
        self.symbol.paint(painter, font, x0, y)
        x1 = x0 + rs.width() / 2 - ra.left()
        self.args.paint(painter, font, x1, y)

class DerivativeElement():
    def __init__(self, diffs, content):
        dl = [[diffs[0], 1]]
        for diff in diffs[1:]:
            if diff == dl[-1][0]:
                dl[-1][1] += 1
            else:
                dl.append([diff, 1])
        if len(dl) == 1:
            d = 'd'
        else:
            d = '\u2202'
        symbol = DivisionElement(SymbolElement(d + "^" + str(sum([i[1] for i in dl]))),
            SymbolElement(''.join([d + str(i[0]) + ("^" + str(i[1]) if i[1] > 1 else '') for i in dl])))
        self.f = FunctionElement(symbol, content)

    def boundingRect(self, font):
        return self.f.boundingRect(font)

    def paint(self, painter, font, x, y):
        self.f.paint(painter, font, x, y)