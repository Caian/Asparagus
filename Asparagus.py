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
from AsparagramLoader import AsparagramLoader

def main():
    printer = UI.init()
    loader = AsparagramLoader(sys.argv[1])
    engine = T3Engine(printer)
    engine.load(loader)
    sys.exit(UI.run())

if __name__ == '__main__':
    main()
