#!/usr/bin/python3

#  Globals.py
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

import sympy

def time(symbols): 
    return symbols.getSymbol('$global', 'time', nonnegative=True)

time_alias = 't'

def gravity(symbols): 
    return (
        symbols.getSymbol('$global', 'gravity.value', nonnegative=True),
        symbols.getSymbol('$global', 'gravity.theta')
    )

gravity_alias = 'g'

def isTimeConstant(s, symbols):
    s = sympy.simplify(s)
    if s == time(symbols):
        return False
    args = s.args
    for arg in args:
        if not isTimeConstant(arg, symbols):
            return False
    return True

def no_alias(t):
    return t

def getObjName(name):
    return name

def getAttachProp(objname, prop):
    return 'attach.%s.%s' % (objname, prop)

def getPropString(objname, prop):
    return '%s.%s' % (objname, prop)

def norm2d(a):
    return sympy.simplify(sympy.sqrt(a[0]**2+a[1]**2))

def cross2d(a, b):
    return sympy.simplify(a[0]*b[1]-b[0]*a[1])

def dot2d(a, b):
    return sympy.simplify(a[0]*b[0]+a[1]*b[1])

def ssign(a):
    return sympy.simplify(sympy.sign(a))
