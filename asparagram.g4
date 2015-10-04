//  asparagram.g4
//
//  Copyright (C) 2015 Caian Benedicto <caianbene@gmail.com>
//
//  This file is part of Asparagus
//
//  Asparagus is free software; you can redistribute it and/or modify it 
//  under the terms of the GNU General Public License as published by 
//  the Free Software Foundation; either version 2, or (at your option)
//  any later version.
//
//  Asparagus is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.

grammar asparagram;

// Root

rlRoot : rlGlobStmt? rlStmt*
       ;

// First level statements

rlStmt : rlObjStmt
       | rlDynStmt
       ;

rlGlobStmt : TKGLOB rlGlobStmts* TKEND
           ;

rlObjStmt : TKOBJ TKID TKAT TKLPAR rlPos TKRPAR TKIS TKID (TKLPAR rlNPropList TKRPAR)? rlObjStmts* TKEND
          ;

rlDynStmt : TKDYN TKID TKIS TKID (TKLPAR rlNPropList TKRPAR)? rlConnection+ rlDynStmts* TKEND
          ;

// Second level global, object and dynamic statements

rlGlobStmts : rlCallStmt
            | rlSetStmt
            ;

rlObjStmts : rlCallStmt
           | rlSetStmt
           | rlPlaceStmt
           ;

rlDynStmts : rlCallStmt
           | rlSetStmt
           ;

rlCallStmt : TKCALL rlProperty TKID
           ;

rlSetStmt : TKSET rlProperty rlValue
          ;

rlPlaceStmt : TKPLC rlProperty TKAT rlValue TKREL TKTO TKID
            ;

// Position vector: x, y

rlPos : TKNUM TKCOM TKNUM
      ;

// Property list: prop1=val1,prop2=val2,...

rlNPropList : rlProperty TKEQ TKNUM (TKCOM rlProperty TKEQ TKNUM)*
            ;

// Property something.foo.bar or $.something.bar.foo

rlProperty : (TKID | TKLEAD) (TKDOT TKID)*
           ;

// Value for properties, can be an id, an expression to be 
// evaluated or a number

rlValue : TKID
        | TKEXPR
        | TKNUM
        ;

// Connection field for dynamics

rlConnection : TKCONN TKTO TKID (TKAT rlRef TKLPAR rlOff TKRPAR)?
             ;

// Reference kind

rlRef : TKRECT
      | TKPOL
      ;

rlOff : rlValue TKCOM rlValue
      ;

// add unicode support and \ for latex

// dynamic s1 is spring
//   
// end

// Tokens

TKCALL : 'call' ;
TKSET  : 'set' ;
TKPLC  : 'place' ;
TKGLOB : 'globals' ;
TKREL  : 'relative' ;
TKOBJ  : 'object' ;
TKDYN  : 'dynamic' ;
TKCONN : 'connected' ;
TKRECT : 'rectangular' ;
TKPOL  : 'polar' ;
TKIS   : 'is' ;
TKTO   : 'to' ;
TKAT   : 'at' ;
TKEND  : 'end' ;
TKLEAD : '$' ;
TKEQ   : '=' ;
TKLPAR : '(' ;
TKRPAR : ')' ;
TKCOM  : ',' ;
TKDOT  : '.' ;
TKNUM  : '-'?(([0-9]+('.'?[0-9]+)?) | ('.'[0-9])) ;
TKID   : [a-zA-Z][a-zA-Z0-9_{}]* ;
TKEXPR : '"' ( '\\"' | . )*? '"' ;
// Comments were moved to a pre-processing stage 
// due to the poor performance of nongreedy subrules 
// in the antlr runtime for python
// TKCOMM : '%' ~[\r\n]* -> skip ;
TKWS   : [ \t\r\n]+ -> skip ;

