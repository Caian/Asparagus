#!/usr/bin/python3

#  SymbolPool.py
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
import Globals

class SymbolPool():
    def __init__(self):
        self.replacements = {}

    def fix(self, expr):
        return expr

    def addReplacement(self, objname, property, value):
            key = Globals.getPropString(objname, property)
            #val = str(value)
            #expr = sympy.parsing.sympy_parser.parse_expr(val)
            #expr = self.fix(expr)
            expr = value
            self.replacements[key] = expr

    def getSymbol(self, objname, property, nonnegative=False):
        key = Globals.getPropString(objname, property)
        r = self.replacements.get(key, key)
        if type(r) == str:
            return sympy.Symbol(key, nonnegative=nonnegative)
        else:
            return sympy.Number(r)

    def getFunction(self, objname, property, args=[], nonnegative=False):
        key = Globals.getPropString(objname, property)
        r = self.replacements.get(key, None)
        if r == None:
            # There is no replacement, create a function
            f = sympy.Function(key, nonnegative=nonnegative)
            if len(args) > 0:
                return f(*args)
            else:
                return f
        elif type(r) == str:
            # A replacement here means constant symbol
            return sympy.Symbol(r, nonnegative=nonnegative)
        else:
            return sympy.Number(r)
