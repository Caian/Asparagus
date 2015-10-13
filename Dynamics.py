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
from Globals import convertAttachment

# Base class for dynamics, contains only a name
class Dynamic:
    def __init__(self, name, symbols):
        self.symbols = symbols
        self.name = str(name)

    def mkattach(self, obj, mode = 'p'):
        if mode == 'p':
            dname = Globals.getAttachProp(obj['$.name'], 'd')
            tname = Globals.getAttachProp(obj['$.name'], 'theta')
            # The angle will always be constant and relative to the 
            # angular position of the body
            t = self.symbols.getSymbol(self.name, tname)
            d = self.symbols.getSymbol(self.name, dname, nonnegative=True)
            # (distance from center of mass, angle)
            return (d, t, mode)
        elif mode == 'r':
            xname = Globals.getAttachProp(obj['$.name'], 'x')
            yname = Globals.getAttachProp(obj['$.name'], 'y')
            # Without moment of inertia, the attachment position will be constant 
            x = self.symbols.getSymbol(self.name, xname)
            y = self.symbols.getSymbol(self.name, yname)
            # (x distance from center of mass, y distance from center of mass)
            return (x, y, mode)
        else:
            raise Exception('invalid attachment mode %s' % str(mode))

    def getLEqns(self):
        # Algebraic Links
        return ()
    
    def simplify1DD(self, expr):
        return expr
        
    def simplify1DL(self, linkeqns):
        return linkeqns

    def getAttachment(self, obj, mode):
        # (distance from center of mass, angle)
        return (None, None) 

#                                                           #
###################### Linear Dynamics ######################
#                                                           #
        
# One-body force that does not depend on any variable 
# of the system other than, possibly, time
class ForceDynamic(Dynamic):
    def __init__(self, name, att, roll, symbols):
        Dynamic.__init__(self, name, symbols)
        self.theta = self.symbols.getSymbol(self.name, 'theta')
        self.obj = att[0]
        self.att = self.mkattach(att[0], att[1])
        self.roll = roll

    def getFSym(self):
        # Not actually nonnegative, but makes analysis easier
        return self.symbols.getSymbol(self.name, 'F', nonnegative=True)
    
    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getFSym(), self.theta, 'roll' if self.roll else '')

    def getAttachment(self, obj, mode):
        if obj != self.obj:
            raise Exception('invalid object')
        # (distance from center of mass, angle)
        return convertAttachment(self.att, mode)
    
# One-body weight dynamic
class WeightDynamic(Dynamic):
    def __init__(self, name, att, symbols):
        Dynamic.__init__(self, name, symbols)
        self.obj = att[0]
        self.att = self.mkattach(att[0], att[1])

    def getFSym(self):
        return self.obj['tr.mass'] * Globals.gravity(self.symbols)[0]
    
    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getFSym(), Globals.gravity(self.symbols)[1], '')

    def getAttachment(self, obj, mode):
        if obj != self.obj:
            raise Exception('invalid object')
        # (distance from center of mass, angle)
        return convertAttachment(self.att, mode)
        
# Base class for dynamics that connect two objects
class PairDynamic(Dynamic):
    def __init__(self, name, atta, rolla, attb, rollb, symbols):
        Dynamic.__init__(self, name, symbols)
        self.obja = atta[0]
        self.objb = attb[0]
        self.atta = self.mkattach(atta[0], atta[1])
        self.attb = self.mkattach(attb[0], attb[1])
        self.rolla = rolla
        self.rollb = rollb

    def getAttachment(self, obj, mode):
        # (distance from center of mass, angle)
        if obj == self.obja:
            return convertAttachment(self.atta, mode)
        if obj == self.objb:
            return convertAttachment(self.attb, mode)
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
    
# Dynamic representing a rigid linear connection between two bodies
# where the traction force is a free variable
class RodDynamic(PairDynamic):
    def __init__(self, name, atta, rolla, attb, rollb, symbols):
        PairDynamic.__init__(self, name, atta, rolla, attb, rollb, symbols)
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
            roll = self.rolla
        elif obj == self.objb:
            theta = self.thetab
            roll = self.rollb
        else:
            raise Exception('invalid object')
        # Return the force in polar coordinates
        return (self.getTSym(), theta, 'roll' if roll else '')

    def getLEqns(self):
        # Algebraic Links
        d = self.getDSym()
        l = self.l
        td = self.thetaa
        x1 = self.obja['tr.x']
        y1 = self.obja['tr.y']
        x2 = self.objb['tr.x']
        y2 = self.objb['tr.y']
        a1 = self.obja['rt.angle']
        a2 = self.objb['rt.angle']

        # Convert the attachments to polar, add the body angle
        # and then reconvert to rectangular
        
        att1 = convertAttachment(self.atta, 'p')
        if att1[0] != 0:
            if not self.rolla:
                att1 = (att1[0], a1 + att1[1], att1[2])
                i1, j1, m1 = convertAttachment(att1, 'r')
            else:
                i1, j1, m1 = convertAttachment(att1, 'r')
                attr = (att1[0] * a1, att1[1] + sympy.pi / 2, att1[2])
                ir, jr, mr = convertAttachment(attr, 'r')
                i1 += ir
                j1 += jr
        else:
            i1 = 0
            j1 = 0

        att2 = convertAttachment(self.attb, 'p')
        if att2[0] != 0:
            if not self.rollb:
                att2 = (att2[0], a2 + att2[1], att2[2])
                i2, j2, m2 = convertAttachment(att2, 'r')
            else:
                i2, j2, m2 = convertAttachment(att2, 'r')
                attr = (att2[0] * a2, att2[1] + sympy.pi / 2, att2[2])
                ir, jr, mr = convertAttachment(attr, 'r')
                i2 += ir
                j2 += jr
        else:
            i2 = 0
            j2 = 0

        return [
            sympy.Eq(x2, x1 + i1 + (l+d)*sympy.sin(td) - i2),
            sympy.Eq(y2, y1 + j1 + (l+d)*sympy.cos(td) - j2),
        ]
    
    def simplify1DD(self, expr):
        return expr
        
    def simplify1DL(self, linkeqns):
        return [ ]
    
# Base class for rod dynamics where the traction force 
# may be a function of the position of the bodies
class ActiveDynamic(RodDynamic):
    def __init__(self, name, atta, rolla, attb, rollb, symbols):
        RodDynamic.__init__(self, name, atta, rolla, attb, rollb, symbols)
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
    def __init__(self, name, atta, rolla, attb, rollb, symbols):
        ActiveDynamic.__init__(self, name, atta, rolla, attb, rollb, symbols)
        self.k = self.symbols.getSymbol(self.name, 'k', nonnegative=True)
        
    def getTSym(self):
        return self.k * self.getDSym()
    
# Dampener Dynamic, where the traction force is a 
# function of the velocity of the bodies
class DampenerDynamic(ActiveDynamic):
    def __init__(self, name, atta, rolla, attb, rollb, symbols):
        ActiveDynamic.__init__(self, name, atta, rolla, attb, rollb, symbols)
        self.b = self.symbols.getSymbol(self.name, 'b', nonnegative=True)
        
    def getTSym(self):
        return self.b * self.getDSym().diff(Globals.time(self.symbols))


#                                                            #
###################### Angular Dynamics ######################
#                                                            #

# One-body torque that does not depend on any variable 
# of the system other than, possibly, time
class TorqueDynamic(Dynamic):
    def __init__(self, name, obj, flipped, symbols):
        Dynamic.__init__(self, name, symbols)
        self.flipped = flipped
        self.obj = obj

    def getFSym(self):
        # Not actually nonnegative, but makes analysis easier
        return self.symbols.getSymbol(self.name, 'T', nonnegative=True)
    
    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')
        # Return the torque in polar coordinates
        f = self.getFSym()
        return (f if not self.flipped else -f, None, '')

# Dynamic representing a rigid angular connection between two bodies
# where the traction force is a free variable
class BeltDynamic(PairDynamic):
    def __init__(self, name, atta, attb, symbols, crossed):
        PairDynamic.__init__(self, name, atta, attb, symbols)
        # r1a1 = r2a2 if not crossed, otherwise r1a1 = -r2a2
        self.crossed = crossed
        
    def getTSym(self):
        return self.symbols.getSymbol(self.name, 'T', nonnegative=True)
    
    def getDSym(self):
        return 0
    
    def getDExpr(self, obj):
        # Select the proper attachment
        if obj == self.obja:
            att = self.atta
            # Inverted because of the -1 inherent from the torque 
            # direction with respect to the reference
            mul = 1 if self.crossed else -1 
        elif obj == self.objb:
            att = self.attb
            mul = 1
        else:
            raise Exception('invalid object')

        att1 = convertAttachment(att, 'p')
        if att1[0] != 0:
            att1 = (att1[0], a1 + att1[1], att1[2])
            i1, j1, m1 = convertAttachment(att1, 'r')
        else:
            raise Exception('coupling radius of %s to %s is zero' % (self.name, obj['$.name']))

        # Return a pure torque
        return (mul * i1 * self.getTSym(), None, '')

    def getLEqns(self):
        # Algebraic Links
        a1 = self.obja['rt.angle']
        a2 = self.objb['rt.angle']

        # Convert the attachments to polar, add the body angle
        # and then reconvert to rectangular
        
        att1 = convertAttachment(self.atta, 'p')
        if att1[0] != 0:
            att1 = (att1[0], a1 + att1[1], att1[2])
            i1, j1, m1 = convertAttachment(att1, 'r')
        else:
            raise Exception('coupling radius of %s to %s is zero' % (self.name, self.obja['$.name']))

        att2 = convertAttachment(self.attb, 'p')
        if att2[0] != 0:
            att2 = (att2[0], a2 + att2[1], att2[2])
            i2, j2, m2 = convertAttachment(att2, 'r')
        else:
            raise Exception('coupling radius of %s to %s is zero' % (self.name, self.objb['$.name']))

        return [
            sympy.Eq(a2, (i1 / i2) * a1) if not self.crossed else
            sympy.Eq(a2, -(i1 / i2) * a1)
        ]
    
    def simplify1DD(self, expr):
        return expr
        
    def simplify1DL(self, linkeqns):
        return linkeqns
    
# Base class for angular dynamics where the torque
# may be a function of the position of the bodies
class ActiveAngularDynamic(Dynamic):
    def __init__(self, name, obj, symbols):
        ActiveAngularDynamic.__init__(self, name, symbols)
        self.obj = obj

    def getDSym(self):
        return self.obj['rt.angle']

    def getDExpr(self, obj):
        if obj != self.obj:
            raise Exception('invalid object')

        # Return a pure torque
        return (self.getTSym(), None, '')

    def getLEqns(self):
        return [ ]

# Angular Spring Dynamic, where the torque is a 
# function of the angular position of the body
class AngularSpringDynamic(ActiveAngularDynamic):
    def __init__(self, name, obj, symbols):
        AngularSpringDynamic.__init__(self, name, obj, symbols)
        self.k = self.symbols.getSymbol(self.name, 'k', nonnegative=True)
        
    def getTSym(self):
        return -self.k * self.getDSym()
    
# Anglar Dampener Dynamic, where the traction force is a 
# function of the velocity of the bodies
class AngularDampenerDynamic(ActiveAngularDynamic):
    def __init__(self, name, obj, symbols):
        AngularDampenerDynamic.__init__(self, name, obj, symbols)
        self.b = self.symbols.getSymbol(self.name, 'b', nonnegative=True)
        
    def getTSym(self):
        return -self.b * self.getDSym().diff(Globals.time(self.symbols))