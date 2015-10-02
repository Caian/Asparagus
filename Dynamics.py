#!/usr/bin/python3

#  Dynamics.py
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

# Just need this for some angle inferences
from Globals import isTimeConstant

# Base class for dynamics, contains only a name
class Dynamic:
    def __init__(self, name, symbols):
        self.symbols = symbols
        self.name = str(name)

    def mkattach(self, obj, mode = 'p'):
        if mode == 'p':
            d = self.symbols.getSymbol(self.name, 'attach.%s.d' % obj['$.name'], nonnegative=True)
            # Without moment of inertia, the angle of the attachment will be constant 
            if obj['rt.mass'] == 0:
                t = self.symbols.getSymbol(self.name, 'attach.%s.theta' % obj['$.name'])
            else:
                t = self.symbols.getFunction(self.name, 'attach.%s.theta' % obj['$.name'], [Globals.time(self.symbols)])
            # (distance from center of mass, angle)
            return (d, t, mode)
        elif mode == 'r':
            # Without moment of inertia, the attachment position will be constant 
            if obj['rt.mass'] == 0:
                x = self.symbols.getSymbol(self.name, 'attach.%s.x' % obj['$.name'])
                y = self.symbols.getSymbol(self.name, 'attach.%s.y' % obj['$.name'])
            else:
                x = self.symbols.getFunction(self.name, 'attach.%s.x' % obj['$.name'], [Globals.time(self.symbols)])
                y = self.symbols.getFunction(self.name, 'attach.%s.y' % obj['$.name'], [Globals.time(self.symbols)])
            # (x distance from center of mass, y distance from center of mass)
            return (x, y, mode)
        else:
            raise Exception('invalid attachment mode %s' % str(mode))

    def convertAttachment(self, att, mode = 't'):
        m = att[2]
        if mode == m:
            return (att[0], att[1])
        elif mode == 'r':
            if m == 'p':
                d = att[0]
                t = att[1]
                return (d*sympy.sin(t), d*sympy.cos(t))
            else:
                raise Exception('invalid attachment mode %s' % str(m))
        elif mode == 'p':
            if m == 'r':
                x = att[0]
                y = att[0]
                # TODO remember to flip y during c->r
                # check theta direction
                return (sympy.sqrt(x**2+y**2), sympy.atan2(x, y))
            else:
                raise Exception('invalid attachment mode %s' % str(m))
        else:
            raise Exception('invalid attachment mode %s' % str(mode))

    def getLEqns(self):
        # Algebraic Links
        return ()
    
    def getIEqns(self):
        # Initial Conditions
        return ()
        
    def simplify1DD(self, expr):
        return expr
        
    def simplify1DL(self, linkeqns):
        return linkeqns

    def getAttachment(self, obj, mode):
        # (distance from center of mass, angle)
        return (None, None) 
        
# One-body force that does not depend on any variable 
# of the system other than, possibly, time
class ForceDynamic(Dynamic):
    def __init__(self, name, obj, symbols):
        Dynamic.__init__(self, name, symbols)
        self.theta = self.symbols.getSymbol(self.name, 'theta')
        self.obj = obj
        self.att = self.mkattach(obj)

    def getFSym(self):
        # Not actually nonnegative, but makes analysis easier
        return self.symbols.getSymbol(self.name, 'F', nonnegative=True)
    
    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getFSym(), self.theta)

    def getAttachment(self, obj, mode):
        if obj != self.obj:
            raise Exception('invalid object')
        # (distance from center of mass, angle)
        return self.convertAttachment(self.att, mode)
    
# One-body weight dynamic
class WeightDynamic(Dynamic):
    def __init__(self, name, obj, symbols):
        Dynamic.__init__(self, name, symbols)
        self.obj = obj

    def getFSym(self):
        return self.obj['tr.mass'] * Globals.gravity(self.symbols)[0]
    
    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getFSym(), Globals.gravity(self.symbols)[1])

    def getAttachment(self, obj, mode):
        if obj != self.obj:
            raise Exception('invalid object')
        # (distance from center of mass, angle)
        return (0, 0)
        
# Base class for dynamics that connect two objects
class PairDynamic(Dynamic):
    def __init__(self, name, obja, objb, symbols):
        Dynamic.__init__(self, name, symbols)
        self.obja = obja
        self.objb = objb
        self.atta = self.mkattach(obja)
        self.attb = self.mkattach(objb)

    def getAttachment(self, obj, mode):
        # (distance from center of mass, angle)
        if obj == self.obja:
            return self.convertAttachment(self.atta, mode)
        if obj == self.objb:
            return self.convertAttachment(self.attb, mode)
        raise Exception('invalid object')
        
    #def getDist(self):
    #    return sympy.sqrt(
    #        (self.objb['tr.x'] - self.obja['tr.x'])**2 +
    #        (self.objb['tr.y'] - self.obja['tr.y'])**2
    #    )
    
    #def getLength(self):
    #    return sympy.sqrt(
    #        (self.objb['tr.x'].subs(Globals.time,0) - self.obja['tr.x'].subs(Globals.time,0))**2 +
    #        (self.objb['tr.y'].subs(Globals.time,0) - self.obja['tr.y'].subs(Globals.time,0))**2
    #    )
    
# Dynamic representing a rigid connection between two bodies
# where the traction force is a free variable
class RodDynamic(PairDynamic):
    def __init__(self, name, obja, objb, symbols):
        PairDynamic.__init__(self, name, obja, objb, symbols)
        self.l = self.symbols.getSymbol(self.name, 'l', nonnegative=True)
        self.thetaa = self.symbols.getFunction(self.name, 'thetaa', [Globals.time(self.symbols)])
        self.thetab = self.thetaa + sympy.pi
        
    def getTSym(self):
        return self.symbols.getSymbol(self.name, 'T', nonnegative=True)
    
    def getDSym(self):
        return 0
    
    def getDExpr(self, obj):
        # Select the proper theta
        if obj == self.obja:
            theta = self.thetaa
        elif obj == self.objb:
            theta = self.thetab
        else:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getTSym(), theta)
    
    def getLEqns(self):
        # Algebraic Links
        d = self.getDSym()
        l = self.l
        td = self.thetaa
        x1 = self.obja['tr.x']
        y1 = self.obja['tr.y']
        x2 = self.objb['tr.x']
        y2 = self.objb['tr.y']
        # attachment A
        i1, j1 = self.convertAttachment(self.atta, 'r')
        # attachment B
        i2, j2 = self.convertAttachment(self.attb, 'r')
        return [
            sympy.Eq(x2, x1 + i1 + (l+d)*sympy.sin(td)) - i2,
            sympy.Eq(y2, y1 + j1 + (l+d)*sympy.cos(td)) - j2,
        ]
    
    def getIEqns(self):
        # Initial Condition
        return (
            sympy.Eq(self.l, self.getLength()),
        )
    
    def simplify1DD(self, expr):
        return expr
        
    def simplify1DL(self, linkeqns):
        return [ ]
    
# Base class for rod dynamics where the traction force 
# may be a function of the position of the bodies
class ActiveDynamic(RodDynamic):
    def __init__(self, name, obja, objb, symbols):
        RodDynamic.__init__(self, name, obja, objb, symbols)
        self.d = self.symbols.getFunction(self.name, 'd', [Globals.time(self.symbols)])
    
    def getDSym(self):
        return self.d

    def simplify1DD(self, expr):
        # Place the offsets of the objects relative to their reference 
        # frame position, so constant position objects have a relative 
        # position of zero
        xb = 0 if isTimeConstant(self.objb['tr.x'], self.symbols) else self.objb['tr.x']
        xa = 0 if isTimeConstant(self.obja['tr.x'], self.symbols) else self.obja['tr.x']
        # b.x = a.x + (l + d)*sin(theta_a)
        # d = b.x - a.x
        return expr.subs(self.d, xb - xa)

# Spring Dynamic, where the traction force is a 
# function of the position of the bodies
class SpringDynamic(ActiveDynamic):
    def __init__(self, name, obja, objb, symbols):
        ActiveDynamic.__init__(self, name, obja, objb, symbols)
        self.k = self.symbols.getSymbol(self.name, 'k', nonnegative=True)
        
    def getTSym(self):
        return self.k * self.getDSym()
    
# Spring Dynamic, where the traction force is a 
# function of the velocity of the bodies
class DampenerDynamic(ActiveDynamic):
    def __init__(self, name, obja, objb, symbols):
        ActiveDynamic.__init__(self, name, obja, objb, symbols)
        self.b = self.symbols.getSymbol(self.name, 'b', nonnegative=True)
        
    def getTSym(self):
        return self.b * self.getDSym().diff(Globals.time(self.symbols))
