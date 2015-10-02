#!/usr/bin/python3

#  Asparagus.py
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

import sys, UI
from T3Engine import T3Engine

class dummy_loader():
    def __init__(self):
        self.i = 0
        self.stmnts = [
            {
                'type' : 'globals',
                'data' : {
                    'name' : '$global'
                },
                'aliases' : {
                    'time' : 't',
                    'gravity.value' : 'g',
                },
                'properties' : {
                    'gravity.theta' : 0,
                }
            },
            { 
                'type' : 'object', 
                'data' : { 
                    'name' : 'box1', 
                    'posx' : 20, 
                    'posy' : -5, 
                    'posa' : 0,
                    'shape' : { 
                        'type' : 'box',
                        'width' : 100,
                        'height' : 100,
                        'angle' : 0
                    } 
                },
                'properties' : {
                    'tr.y' : 'Y',
                    'rt.mass' : 0
                },
                'aliases' : {
                    'tr.mass' : 'm_1',
                    '$.name' : 'm_1',
                    'tr.x' : 'w'
                }
            },
            { 
                'type' : 'object', 
                'data' : { 
                    'name' : 'box2', 
                    'posx' : 250, 
                    'posy' : -5, 
                    'posa' : 0,
                    'shape' : { 
                        'type' : 'box',
                        'width' : 100,
                        'height' : 100,
                        'angle' : 0
                    } 
                },
                'properties' : {
                    'tr.y' : 'Y',
                    'rt.mass' : 0
                },
                'aliases' : {
                    'tr.mass' : 'm_2',
                    '$.name' : 'm_2',
                    'tr.x' : 'x',
                    'tr.y' : 'y'
                }
            },
            { 
                'type' : 'object', 
                'data' : { 
                    'name' : 'wall', 
                    'posx' : -150, 
                    'posy' : -5, 
                    'posa' : 0,
                    'shape' : { 
                        'type' : 'wall',
                        'width' : 0,
                        'height' : 200
                    } 
                },
                'properties' : {
                    'tr.mass' : 0,
                    'tr.x' : 'Xw',
                    'tr.y' : 'Y',
                    'rt.mass' : 0
                }
            },
            { 
                'type' : 'object', 
                'data' : { 
                    'name' : 'ball', 
                    'posx' : 400, 
                    'posy' : -150, 
                    'posa' : 0,
                    'shape' : { 
                        'type' : 'ball',
                        'radius' : 21.21
                    }
                },
                'properties' : {
                    'rt.mass' : 0
                },
                'aliases' : {
                    'tr.mass' : 'M',
                    '$.name' : '',
                    'tr.x' : 'u',
                    'tr.y' : 'v'
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'F1',
                    'dynamic' : 'force',
                    'bodies' : [ 'box2' ],
                    'offset' : (50, 0, 100, 0)
                },
                'aliases' : {
                    'F' : 'F'
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'W2',
                    'dynamic' : 'weight',
                    'bodies' : [ 'ball' ],
                    'offset' : (0, -21.21, 0, -71.21)
                },
                'aliases' : {
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'S1',
                    'dynamic' : 'spring',
                    'bodies' : [ 'wall', 'box1' ],
                    'offset' : (0, 30, -50, 30)
                },
                'aliases' : {
                    'k' : 'k_1'
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'S2',
                    'dynamic' : 'spring',
                    'bodies' : [ 'box1', 'box2' ],
                    'offset' : (50, 0, -50, 0)
                },
                'aliases' : {
                    'k' : 'k_2'
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'D2',
                    'dynamic' : 'dampener',
                    'bodies' : [ 'box1', 'wall' ],
                    'offset' : (-50, -30, 0, -30)
                },
                'aliases' : {
                    'b' : 'b_1'
                }
            },
            {
                'type' : 'dynamic',
                'data' : {
                    'name' : 'R1',
                    'dynamic' : 'rod',
                    'bodies' : [ 'box2', 'ball' ],
                    'offset' : (0, -50, 0, 0)
                },
                'properties' : {
                    'showangles' : True
                },
                'aliases' : {
                    'T' : 'T',
                    'l' : 'L',
                    'thetaa' : '\u03B8'
                }
            }
        ]

    def getAliases(self):
        return {
        }

    def nextStmt(self):
        if self.i == len(self.stmnts):
            return None
        s = self.stmnts[self.i]
        self.i += 1
        return s

def main():
    printer = UI.init()
    engine = T3Engine(printer)
    engine.load(dummy_loader())
    sys.exit(UI.run())

if __name__ == '__main__':
    main()
