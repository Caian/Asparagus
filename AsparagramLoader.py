#!/usr/bin/python3

#  AsparagramLoader.py
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

from antlr4 import *
from asparagramLexer import asparagramLexer
from asparagramParser import asparagramParser
from asparagramVisitor import asparagramVisitor

class AsparagramLoader(asparagramVisitor):
    def __init__(self, filename):
        with open(filename, 'r') as file:
            data = file.read()

        # Process comments manually 
        while True:
            i = data.find('%')
            if i == -1:
                break
            j = data.find('\n', i)
            if j == -1:
                data = data[:i]
            else:
                data = data[:i] + data[j:]

        # Parse the file
        input = InputStream(data)
        lexer = asparagramLexer(input)
        stream = CommonTokenStream(lexer)
        parser = asparagramParser(stream)
        tree = parser.rlRoot()

        # Walk the tree
        self.stmts = self.visit(tree)
        self.i = 0

    def nextStmt(self):
        if self.i == len(self.stmts):
            return None
        s = self.stmts[self.i]
        self.i += 1
        return s

    # Visit a parse tree produced by asparagramParser#rlRoot.
    def visitRlRoot(self, ctx:asparagramParser.RlRootContext):
        stmts = []
        for i in range(ctx.getChildCount()):
            stmts.append(self.visit(ctx.getChild(i)))
        return stmts

    # Visit a parse tree produced by asparagramParser#rlGlobStmt.
    def visitRlGlobStmt(self, ctx:asparagramParser.RlGlobStmtContext):
        props = []
        aliases = []
        for i in range(1, ctx.getChildCount() - 1):
            stmt = self.visit(ctx.getChild(i))
            (props if stmt[0] == 'set' else aliases).append(stmt[1:])

        # Build the statement clause
        return {
            'type' : 'globals',
            'data' : {
                'name' : '$global',
            },
            'properties' : props,
            'aliases' : aliases
        }

    # Visit a parse tree produced by asparagramParser#rlObjStmt.
    def visitRlObjStmt(self, ctx:asparagramParser.RlObjStmtContext):
        name = ctx.getChild(1).getText()
        pos = self.visit(ctx.getChild(4))
        obj = ctx.getChild(7).getText()
        
        # Test if the property list of the object is present
        if self.visit(ctx.getChild(8)) == None and ctx.getChild(8).getText() == '(':
            # Get shape and set the statements position to after ')'
            shape = self.visit(ctx.getChild(9))
            stpos = 11
        else:
            # No shape, so this must be the start of the statements
            shape = {}
            stpos = 8

        # Object type is also part of the shape
        shape['type'] = obj

        # Go though all statements until 'end'
        props = []
        aliases = []
        for i in range(stpos, ctx.getChildCount() - 1):
            stmt = self.visit(ctx.getChild(i))
            (props if stmt[0] == 'set' else aliases).append(stmt[1:])

        # Build the statement clause
        return {
            'type' : 'object',
            'data' : {
                'name' : name,
                'pos' : pos,
                'shape' : shape
            },
            'properties' : props,
            'aliases' : aliases
        }


    # Visit a parse tree produced by asparagramParser#rlDynStmt.
    def visitRlDynStmt(self, ctx:asparagramParser.RlDynStmtContext):
        name = ctx.getChild(1).getText()
        dyn = ctx.getChild(3).getText()
        
        # Test if the property list of the dynamic is present
        if self.visit(ctx.getChild(4)) == None and ctx.getChild(4).getText() == '(':
            # Get shape and set the statements position to after ')'
            shape = self.visit(ctx.getChild(5))
            stpos = 7
        else:
            # No shape, so this must be the start of the statements
            shape = {}
            stpos = 4

        # Go though all statements and connections until 'end'
        conn = []
        props = []
        aliases = []
        for i in range(stpos, ctx.getChildCount() - 1):
            stmt = self.visit(ctx.getChild(i))
            if stmt[0] == 'conn':
                conn.append(stmt[1:])
            else:
                (props if stmt[0] == 'set' else aliases).append(stmt[1:])

        # Build the statement clause
        return {
            'type' : 'dynamic',
            'data' : {
                'name' : name,
                'dynamic' : dyn,
                'attach' : conn,
                'offset' : shape
            },
            'properties' : props,
            'aliases' : aliases
        }


    # Visit a parse tree produced by asparagramParser#rlCallStmt.
    def visitRlCallStmt(self, ctx:asparagramParser.RlCallStmtContext):
        name = ctx.getChild(1).getText()
        value = ctx.getChild(2).getText()
        return ('call', name, '' if value == '""' else value)


    # Visit a parse tree produced by asparagramParser#rlSetStmt.
    def visitRlSetStmt(self, ctx:asparagramParser.RlSetStmtContext):
        name = ctx.getChild(1).getText()
        value = ctx.getChild(2).getText()
        return ('set', name, value, None)


    # Visit a parse tree produced by asparagramParser#rlPlaceStmt.
    def visitRlPlaceStmt(self, ctx:asparagramParser.RlPlaceStmtContext):
        name = ctx.getChild(1).getText()
        value = ctx.getChild(3).getText()
        obj = ctx.getChild(6).getText()
        return ('set', name, value, obj)


    # Visit a parse tree produced by asparagramParser#rlPos.
    def visitRlPos(self, ctx:asparagramParser.RlPosContext):
        x = float(ctx.getChild(0).getText())
        y = float(ctx.getChild(2).getText())
        return (x, y)


    # Visit a parse tree produced by asparagramParser#rlNPropList.
    def visitRlNPropList(self, ctx:asparagramParser.RlNPropListContext):
        props = {}
        for i in range(0, ctx.getChildCount(), 4):
            name = ctx.getChild(i).getText()
            value = float(ctx.getChild(i+2).getText())
            # TODO: Repeated warning
            props[name] = value
        return props


    # Visit a parse tree produced by asparagramParser#rlConnection.
    def visitRlConnection(self, ctx:asparagramParser.RlConnectionContext):
        obj = ctx.getChild(2).getText()
        if ctx.getChildCount() > 3:
            ref = self.visit(ctx.getChild(4))
            off = self.visit(ctx.getChild(6))
            return ('conn', obj, ref, off)
        else:
            return ('conn', obj, )


    # Visit a parse tree produced by asparagramParser#rlRef.
    def visitRlRef(self, ctx:asparagramParser.RlRefContext):
        # 2 types of coordinates, polar and rectangular
        r = ctx.getChild(0).getText()
        if r == 'polar':
            return 'p'
        else:
            return 'r'


    # Visit a parse tree produced by asparagramParser#rlOff.
    def visitRlOff(self, ctx:asparagramParser.RlOffContext):
        a = ctx.getChild(0).getText()
        b = ctx.getChild(2).getText()
        return (a, b)