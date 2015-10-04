# Generated from asparagram.g4 by ANTLR 4.5.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .asparagramParser import asparagramParser
else:
    from asparagramParser import asparagramParser

# This class defines a complete generic visitor for a parse tree produced by asparagramParser.

class asparagramVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by asparagramParser#rlRoot.
    def visitRlRoot(self, ctx:asparagramParser.RlRootContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlStmt.
    def visitRlStmt(self, ctx:asparagramParser.RlStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlGlobStmt.
    def visitRlGlobStmt(self, ctx:asparagramParser.RlGlobStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlObjStmt.
    def visitRlObjStmt(self, ctx:asparagramParser.RlObjStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlDynStmt.
    def visitRlDynStmt(self, ctx:asparagramParser.RlDynStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlGlobStmts.
    def visitRlGlobStmts(self, ctx:asparagramParser.RlGlobStmtsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlObjStmts.
    def visitRlObjStmts(self, ctx:asparagramParser.RlObjStmtsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlDynStmts.
    def visitRlDynStmts(self, ctx:asparagramParser.RlDynStmtsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlCallStmt.
    def visitRlCallStmt(self, ctx:asparagramParser.RlCallStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlSetStmt.
    def visitRlSetStmt(self, ctx:asparagramParser.RlSetStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlPlaceStmt.
    def visitRlPlaceStmt(self, ctx:asparagramParser.RlPlaceStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlPos.
    def visitRlPos(self, ctx:asparagramParser.RlPosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlNPropList.
    def visitRlNPropList(self, ctx:asparagramParser.RlNPropListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlProperty.
    def visitRlProperty(self, ctx:asparagramParser.RlPropertyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlValue.
    def visitRlValue(self, ctx:asparagramParser.RlValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlConnection.
    def visitRlConnection(self, ctx:asparagramParser.RlConnectionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlRef.
    def visitRlRef(self, ctx:asparagramParser.RlRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by asparagramParser#rlOff.
    def visitRlOff(self, ctx:asparagramParser.RlOffContext):
        return self.visitChildren(ctx)



del asparagramParser