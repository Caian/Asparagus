#!/usr/bin/python3

#  T3Engine.py
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
from sympy.printing.str import StrPrinter
import SymbolPool
import Dynamics
import Globals

# Just need this for some angle inferences
from Globals import isTimeConstant

class AliasPrinter(StrPrinter):
    def __init__(self, aliases):
        super(AliasPrinter, self).__init__()
        self.aliases = aliases

    def _print_Symbol(self, expr):
        s = self.aliases.get(expr, expr.name)
        return self.aliases.get(s, s)
    
    def _print_Function(self, expr):
        s = self.aliases.get(expr, str(expr.func))
        return self.aliases.get(s, s) + '(' + ', '.join([str(a) for a in expr.args]) + ')'

# Choo-Choooo

class T3Engine():
    def __init__(self, printing_iface):
        self.printer = printing_iface
        self.scene = None
        self.aliases = { }
        self.symbols = None
        a = self.aliases
        sympy.Basic.__str__ = lambda self: AliasPrinter(a).doprint(self)

    def mkobject(self, name):
        s = str(name)
        return {
            '$.name' : Globals.getObjName(s),
            'tr' : self.symbols.getFunction(s, 'tr', [Globals.time(self.symbols)]),
            'tr.x' : self.symbols.getFunction(s, 'tr.x', [Globals.time(self.symbols)]),
            'tr.y' : self.symbols.getFunction(s, 'tr.y', [Globals.time(self.symbols)]),
            'tr.mass' : self.symbols.getSymbol(s, 'tr.mass', nonnegative=True),
            'tr.frame' : {
                'theta' : self.symbols.getSymbol(s, 'tr.theta')
            },
            'rt.mass' : self.symbols.getSymbol(s, 'rt.mass', nonnegative=True),
            'rt.angle' : self.symbols.getFunction(s, 'rt.angle', [Globals.time(self.symbols)]),
            'rt.frame' : {
                'dir' : 1,
            }
        }

    def hasObject(self, name):
        return name in self.scene['attachments'].keys()

    def getObject(self, name):
        for obj in self.scene['objects']:
            if obj['$.name'] == name:
                return obj
        raise Exception('could not find object named %s' % name)

    def inferPairAngle(self, obja, atta, objb, attb):
        x1 = obja['tr.x']
        y1 = obja['tr.y']
        x2 = objb['tr.x']
        y2 = objb['tr.y']
        a1 = obja['rt.angle']
        a2 = objb['rt.angle']

        # Convert the attachments to polar, add the body angle
        # and then reconvert to rectangular
        
        att1 = Globals.convertAttachment(atta, 'p')
        if att1[0] != 0:
            att1 = (att1[0], a1 + att1[1], att1[2])
            i1, j1, m1 = Globals.convertAttachment(att1, 'r')
        else:
            i1 = 0
            j1 = 0

        att2 = Globals.convertAttachment(attb, 'p')
        if att2[0] != 0:
            att2 = (att2[0], a2 + att2[1], att2[2])
            i2, j2, m2 = Globals.convertAttachment(att2, 'r')
        else:
            i2 = 0
            j2 = 0

        dx = sympy.sympify((x2 + i2) - (x1 + i1))
        dy = sympy.sympify((y2 + j2) - (y1 + j1))

        return sympy.sympify(sympy.atan2(dx, dy))

    def assertPairAngle(self, dyn):
        x1 = dyn.obja['tr.x']
        y1 = dyn.obja['tr.y']
        x2 = dyn.objb['tr.x']
        y2 = dyn.objb['tr.y']
        a1 = dyn.obja['rt.angle']
        a2 = dyn.objb['rt.angle']
        thetaa = dyn.thetaa
        name = dyn.name

        if not isTimeConstant(thetaa, self.symbols):
            return True

        # Convert the attachments to polar, add the body angle
        # and then reconvert to rectangular
        
        att1 = dyn.getAttachment(dyn.obja, 'p')
        if att1[0] != 0:
            att1 = (att1[0], a1 + att1[1], att1[2])
            i1, j1, m1 = Globals.convertAttachment(att1, 'r')
        else:
            i1 = 0
            j1 = 0

        att2 = dyn.getAttachment(dyn.objb, 'p')
        if att2[0] != 0:
            att2 = (att2[0], a2 + att2[1], att2[2])
            i2, j2, m2 = Globals.convertAttachment(att2, 'r')
        else:
            i2 = 0
            j2 = 0

        dx = sympy.sympify((x2 + i2) - (x1 + i1))
        dy = sympy.sympify((y2 + j2) - (y1 + j1))

        if dx == 0 and sympy.simplify(sympy.Mod(thetaa,sympy.pi)) != 0:
            self.printer.print_diagnostic(2, 'thetaa assertion failed for dynamic %s, set=%s, inferred=%s.' % 
                (name, str(thetaa), str(sympy.sympify(sympy.atan2(dx, dy)))))
            return False
        elif dy == 0 and sympy.simplify(sympy.Mod(thetaa+sympy.pi/2,sympy.pi)) != 0:
            self.printer.print_diagnostic(2, 'thetaa assertion failed for dynamic %s, set=%s, inferred=%s.' % 
                (name, str(thetaa), str(sympy.sympify(sympy.atan2(dx, dy)))))
            return False

        return True

    def loadObject(self, name, props, data, aliases):
        pos = data['pos']
        shape = data['shape']
        label = aliases.get('$.name', name)

        # Create a new object and, if it's not already in the scene, add it
        obj = self.mkobject(name)
        
        if self.hasObject(name):
            raise Exception('the scene already contains an object named %s' % name)

        self.scene['objects'].append(obj)
        self.scene['attachments'][name] = [ ]

        # Fill the replacement table
        for k, v in aliases.items():
            self.aliases[obj[k]] = v

        # Print the object
        self.printer.print_object(name, pos, shape, label, props)

    def loadDynamic(self, name, props, data, aliases):
        dyn = data['dynamic']
        bodies = [self.getObject(n[0]) for n in data['attach']]
        attmodes = [n[1] if len(n) > 1 else 'p' for n in data['attach']]
        attoffs = [n[2] if len(n) > 1 else None for n in data['attach']]
        offs = data['offset']
        showangles = props.get('showangles', False)

        # A few assert funtions...
        def assert_bodies(name, n):
            if len(bodies) != n:
                raise Exception('%s dynamic expects %d body, provided %d' % (name, n, len(bodies)))
        def assert_offs(name, n):
            if len(offs) != n:
                raise Exception('%s dynamic expects %d offsets, provided %d' % (name, n, len(offs)))
        def aliasify(s, p):
            alias = aliases.get(s, None)
            if alias != None: 
                self.aliases[p] = alias
            return str(p)

        # Roll assertions

        def get0Rolls(what):
            roll = props.get('roll', None)
            if roll == None:
                roll = props.get('rolla', None)

            if roll == '1' or roll == "1":
                self.printer.print_diagnostic(2, 'dynamic %s does not have roll because it is %s.' % (name, what))

        def get1Roll():
            roll = props.get('roll', None)
            if roll == None:
                roll = props.get('rolla', None)

            if roll == '1' or roll == "1":
                self.printer.print_diagnostic(3, 'dynamic %s set to roll mode on body %s.' % (name, bodies[0]['$.name']))
                roll = True
            return roll

        def get2Rolls():
            rolla = props.get('rolla', None)
            if rolla == '1' or rolla == "1":
                self.printer.print_diagnostic(3, 'dynamic %s set to roll mode on body %s.' % (name, bodies[0]['$.name']))
                rolla = True

            rollb = props.get('rollb', None)
            if rollb == '1' or rollb == "1":
                self.printer.print_diagnostic(3, 'dynamic %s set to roll mode on body %s.' % (name, bodies[1]['$.name']))
                rollb = True
            return (rolla, rollb)

        # Resolve the attachments 
        for b, m, o in zip(bodies, attmodes, attoffs):
            if o != None:
                if m == 'p':
                    ata = Globals.getAttachProp(b['$.name'], 'd')
                    atb = Globals.getAttachProp(b['$.name'], 'theta')
                elif m == 'r':
                    ata = Globals.getAttachProp(b['$.name'], 'x')
                    atb = Globals.getAttachProp(b['$.name'], 'y')

                self.symbols.addReplacement(name, ata, o[0])
                self.symbols.addReplacement(name, atb, o[1])

        # Switch the dynamic type
        if dyn == 'force':
            assert_bodies('force', 1)
            assert_offs('force', 4)

            pos = (offs['x1'], offs['y1'], 
                   offs['x2'], offs['y2'])

            att = (bodies[0], attmodes[0])

            # Constant Force has only one roll
            roll = get1Roll()

            d = Dynamics.ForceDynamic(name, att, roll, self.symbols)

            t = aliasify('theta', d.theta)
            title = aliasify('F', d.getFSym())

        elif dyn == 'weight':
            # TODO ignore offset and force it to center of mass
            assert_bodies('weight', 1)
            assert_offs('weight', 4)

            pos = (offs['x1'], offs['y1'], 
                   offs['x2'], offs['y2'])

            # Weight Force has only no rolls :/
            get0Rolls('weight')
            
            d = Dynamics.WeightDynamic(name, bodies[0], self.symbols)

            title = str(d.getFSym())
            showangles = False # Do not show theta for gravity

        elif dyn == 'rod':
            assert_bodies('rod', 2)
            assert_offs('rod', 4)

            pos = (offs['x1'], offs['y1'], 
                   offs['x2'], offs['y2'])

            att0 = (bodies[0], attmodes[0])
            att1 = (bodies[1], attmodes[1])

            # Rod has two rolls, for a and b points
            rolla, rollb = get2Rolls()
            
            d = Dynamics.RodDynamic(name, att0, rolla, att1, rollb, self.symbols)
            
            aliasify('l', d.l)
            t = aliasify('thetaa', d.thetaa)
            title = aliasify('T', d.getTSym())

        elif dyn == 'spring':
            assert_bodies('spring', 2)
            assert_offs('spring', 4)

            pos = (offs['x1'], offs['y1'], 
                   offs['x2'], offs['y2'])

            att0 = (bodies[0], attmodes[0])
            att1 = (bodies[1], attmodes[1])

            # Spring has two rolls, for a and b points
            rolla, rollb = get2Rolls()

            d = Dynamics.SpringDynamic(name, att0, rolla, att1, rollb, self.symbols)
            
            aliasify('l', d.l)
            aliasify('d', d.d)
            aliasify('T', d.getTSym())
            t = aliasify('thetaa', d.thetaa)
            title = aliasify('k', d.k)

        elif dyn == 'dampener':
            assert_bodies('dampener', 2)
            assert_offs('dampener', 4)

            pos = (offs['x1'], offs['y1'], 
                   offs['x2'], offs['y2'])

            att0 = (bodies[0], attmodes[0])
            att1 = (bodies[1], attmodes[1])

            # Dampener has two rolls, for a and b points
            rolla, rollb = get2Rolls()

            d = Dynamics.DampenerDynamic(name, att0, rolla, att1, rollb, self.symbols)
            
            aliasify('l', d.l)
            aliasify('d', d.d)
            aliasify('T', d.getTSym())
            t = aliasify('thetaa', d.thetaa)
            title = aliasify('b', d.b)

        else:
            raise Exception('unknown dynamic type %s' % dyn)

        # Add dynamic to the list of dynamic in the scene
        self.scene['dynamics'].append(d)

        # Add dynamic to the collection of dynamics of each body
        for body in bodies:
            self.scene['attachments'][body['$.name']].append(d)

        # Draw the dynamic
        self.printer.print_dynamic(name, dyn, pos, title, props)

        # Draw the angle of the dynamic, if specified
        if showangles == '1' or showangles == True:
            self.printer.print_angle(name, t)

    def loadGlobals(self, name, aliases):
        # Fill the replacement table
        for k, v in aliases.items():
            self.aliases[Globals.getPropString(name, k)] = v

    def load(self, scene_loader):
        # Initialize the aliases
        self.printer.print_diagnostic(3, 'initializing alias table for symbols...')
        self.aliases.clear() 

        # Initialize the SymbolPool
        self.printer.print_diagnostic(3, 'initializing symbol pool...')
        self.symbols = SymbolPool.SymbolPool()

        # Initialize the scene
        self.printer.print_diagnostic(3, 'initializing empty scene...')
        self.scene = { 
            'objects' : [ ],
            'dynamics' : [ ], 
            'attachments' : { },
            'fragments' : [],
            'system' : [],
            'refs' : {},
            'equations' : [],
        }

        # Loop through all statements to load the scene
        self.printer.print_diagnostic(3, 'loading scene...')
        while True:
            stmt = scene_loader.nextStmt()
            self.printer.print_diagnostic(4, 'processing statement...')
            if stmt == None:
                break

            stype = stmt['type']
            data = stmt['data']
            name = data['name']
            props = stmt.get('properties', [])
            aliases = stmt.get('aliases', [])

            # Verify aliases
            p = set()
            a = {}

            for alias, val in aliases:
                # See if its already defined
                if alias in p:
                    self.printer.print_diagnostic(2, 'Alias %s already set for %s, later value ignored.' % (alias, name))

                a[alias] = val
                p.add(alias)

            aliases = a

            # Add the properties to the SymbolPool
            # before the creation of the object or dynamic
            p = set()
            a = {}

            for prop, val, ref in props:
                # See if its already defined
                if prop in p:
                    self.printer.print_diagnostic(2, 'Property %s already set for %s, later value ignored.' % (prop, name))

                # Ignore relative placement here
                if ref != None:
                    continue

                a[prop] = val
                p.add(prop)

                self.symbols.addReplacement(name, prop, val)

            props = a

            # Parse the statement content
            if stype == 'object':
                self.printer.print_diagnostic(4, 'statement is object.')
                self.loadObject(name, props, data, aliases)
            elif stype == 'dynamic':
                self.printer.print_diagnostic(4, 'statement is dynamic.')
                self.loadDynamic(name, props, data, aliases)
            elif stype == 'globals':
                self.loadGlobals(name, aliases)
            else:
                raise Exception('unknown statement type %s' % stype)
        self.printer.print_diagnostic(3, 'scene loaded.')

        # Solve the system
        self.solve()

    def solve(self):
        self.assertState()
        self.solveAssembly()
        self.solveIC()
        self.solveRefFrames()
        self.solveEquations()

    def assertState(self):
        for dyn in self.scene['dynamics']:
            if issubclass(type(dyn), Dynamics.RodDynamic): 
                self.assertPairAngle(dyn)

    def solveAssembly(self):
        self.printer.print_diagnostic(3, 'processing system...')

        # System of equations assembly
        self.printer.print_diagnostic(3, 'assembling system fragments...')
        for obj in self.scene['objects']:
            if obj['tr.mass'] == 0 and obj['rt.mass'] == 0:
                self.printer.print_diagnostic(3, 'object %s has no mass or moment of inertia and will be ignored.' % obj['$.name'])
                continue
            expr = {
                'object' : obj,
                'rhs' : [dyn.getDExpr(obj)+(dyn,) for dyn in self.scene['attachments'][obj['$.name']]]
            }
            self.printer.print_diagnostic(4, '%s - %d fragments (%s).' % (obj['$.name'], len(expr['rhs']), 
                ', '.join([dyn[-1].name for dyn in expr['rhs']])))
            self.scene['fragments'].append(expr)

    def solveIC(self):
        # Initial conditions
        self.printer.print_diagnostic(3, 'applying initial conditions... skipped') # TODO: change this

    def solveRefFrames(self):
        # Reference frames
        self.printer.print_diagnostic(3, 'deducing reference frames...')
        for expr in self.scene['fragments']:
            obj = expr['object']
            if len(expr['rhs']) == 0:
                self.printer.print_diagnostic(2, '%s has no dynamics associated.' % obj['$.name'])
                rmode = 0
                tmode = 0
                angle = 0
                dir = 0
            else:
                cx = isTimeConstant(obj['tr.x'], self.symbols)
                cy = isTimeConstant(obj['tr.y'], self.symbols)
                ca = isTimeConstant(obj['rt.angle'], self.symbols)
                if cx and cy and ca:
                    # All axis of movement are locked (all motion variables are constants)
                    self.printer.print_diagnostic(2, '%s is fully locked.' % obj['$.name'])
                    rmode = 0
                    tmode = 0
                    angle = 0
                    dir = 1
                else:
                    rmode = 1
                    tmode = 2
                    angle = 0
                    dir = 1
                    # See if rotation is locked
                    #if ca:
                    #    if obj['rt.mass'] != 0:
                    #        self.printer.print_diagnostic(2, '%s has no rotation but has moment of inertia.' % obj['$.name'])
                    #    rmode = 0
                    #    dir = 0
                    #else:
                    #    rmode = 1
                    #    dir = 1
                    ## Deduce translations
                    #if cx and cy:
                    #    if obj['tr.mass'] != 0:
                    #        self.printer.print_diagnostic(2, '%s has no translation but has mass.' % obj['$.name'])
                    #    tmode = 0
                    #    angle = 0
                    #elif cx:
                    #    # Translation along x axis
                    #    tmode = 1
                    #    angle = sympy.pi / 2
                    #elif cy:
                    #    # Translation along y axis
                    #    tmode = 1
                    #    angle = 0
                    #else:
                    #    # xy free, deduce from dynamics
                    #    # Check if a 2D ref frame is necessary
                    #    # for that all forces must be aligned on the same
                    #    # axis and the angle cannot vary with time
                    #    angle = expr['rhs'][0][1]
                    #    if not isTimeConstant(angle, self.symbols):
                    #        tmode = 2
                    #        angle = 0
                    #    else:
                    #        tmode = 1
                    #        for rhs in expr['rhs'][1:]:
                    #            # simplification of cross product for unit vectors
                    #            # to evaluate if two angles form parallel vectors
                    #            a = rhs[1]
                    #            if isTimeConstant(a, self.symbols) == False or sympy.sin(sympy.simplify(angle-a)) != 0:
                    #                angle = 0
                    #                tmode = 2
                    #                break
            self.printer.print_diagnostic(4, '%s - %d translation DOF (rotated by %s), %d rotation DOF (%s).' % 
                (obj['$.name'], tmode, str(angle), rmode, 'CCW' if dir == 1 else 'CW'))
            self.scene['refs'][obj['$.name']] = (tmode, rmode, angle, dir)

    def solveEquations(self):
        # System of equations
        self.printer.print_diagnostic(3, 'Finishing system of equations...')
        for ei, expr in enumerate(self.scene['fragments']):
            obj = expr['object']
            self.printer.print_diagnostic(3, '(%d/%d) %s...' % (ei+1, len(self.scene['fragments']), obj['$.name']))
            rftmode, rfrmode, rfangle, rfdir = self.scene['refs'][obj['$.name']]
            rhsx = 0
            rhsy = 0
            rhst = 0
            cx = isTimeConstant(obj['tr.x'], self.symbols)
            cy = isTimeConstant(obj['tr.y'], self.symbols)
            ca = isTimeConstant(obj['rt.angle'], self.symbols)
            for i in expr['rhs']:
                force = i[0]
                dyn = i[-1]
                roll = i[2] == 'roll'
                angle = i[1]
                # Compute the force components
                if angle != None:
                    if rftmode == 1:
                        x = sympy.simplify(force*sympy.sin(i[1]))
                        rhsx += dyn.simplify1DD(x)
                    elif rftmode == 2:
                        if not cx:
                            x = sympy.simplify(force*sympy.sin(i[1]))
                            rhsx += x
                        if not cy:
                            y = sympy.simplify(force*sympy.cos(i[1]))
                            rhsy += y
                    if rfrmode != 0 and not ca:
                        # Compute the torque components
                        atd, ata, atm = dyn.getAttachment(obj, 'p')
                        if atd != 0:
                            # Roll dynamics will assume a force perpendicular to the radius vector
                            if not roll:
                                # Compute the torque angle
                                tangle = ata + sympy.pi / 2 + obj['rt.angle']

                                # Compute the projection of the force onto the torque direction
                                torque = sympy.simplify(force * atd * sympy.cos(angle - tangle))
                            else:
                                # Compute the torque of a perpendicular force
                                torque = sympy.simplify(force * atd)
                            rhst += torque

                elif not ca:
                    # The force is actually a torque...
                    rhst += force
                    # Well this is weird...
                    if obj['rt.mass'] == 0:
                        self.printer.print_diagnostic(2, 'pure torque from %s applied to %s which has no moment of inertia.' % (dyn.name, obj['$.name']))
            # Append the translation equations 
            if rftmode != 0:
                if obj['tr.mass'] == 0:
                    self.printer.print_diagnostic(3, 'ignoring translational equations for body %s bacause it has no mass.' % obj['$.name'])
                else:
                    if rftmode == 1:
                        self.scene['equations'].append(sympy.Eq(obj['tr.mass']*sympy.Derivative(obj['tr.x'], 
                            Globals.time(self.symbols), Globals.time(self.symbols)), rhsx))
                    if rftmode == 2:
                        if cx:
                            self.printer.print_diagnostic(3, 'ignoring x-axis translational equation for body %s bacause it is locked.' % obj['$.name'])
                        else:
                            self.scene['equations'].append(sympy.Eq(obj['tr.mass']*sympy.Derivative(obj['tr.x'], 
                                Globals.time(self.symbols), Globals.time(self.symbols)), rhsx))
                        if cy:
                            self.printer.print_diagnostic(3, 'ignoring y-axis translational equation for body %s bacause it is locked.' % obj['$.name'])
                        else:
                            self.scene['equations'].append(sympy.Eq(obj['tr.mass']*sympy.Derivative(obj['tr.y'], 
                                Globals.time(self.symbols), Globals.time(self.symbols)), rhsy))
                    else:
                        raise Exception('unknown reference frame mode')
            # Append the rotation equations 
            if rfrmode != 0:
                if obj['rt.mass'] == 0:
                    self.printer.print_diagnostic(3, 'ignoring rotational equations for body %s bacause it has no moment of inertia.' % obj['$.name'])
                else:
                    if rfrmode == 1:
                        if ca:
                            self.printer.print_diagnostic(3, 'ignoring rotational equation for body %s bacause it is locked.' % obj['$.name'])
                        else:
                            self.scene['equations'].append(sympy.Eq(obj['rt.mass']*sympy.Derivative(obj['rt.angle'], 
                                Globals.time(self.symbols), Globals.time(self.symbols)), rhst))
                    else:
                        raise Exception('unknown reference frame mode')
        # Finish with the link equations
        for di, dyn in enumerate(self.scene['dynamics']):
            self.printer.print_diagnostic(3, '(%d/%d) %s...' % (di+1, len(self.scene['dynamics']), dyn.name))
            les = dyn.getLEqns()
            for le in les:
                le = sympy.simplify(le)
                if le == True:
                    self.printer.print_diagnostic(3, 'link equation was reduced to 0 == 0 due to constraints and will be ignored.')
                else:
                    self.scene['equations'].append(le)
        seq = []
        for eq in self.scene['equations']:
            seq.append(str(eq))
        self.printer.print_diagnostic(3, 'system ready.')
