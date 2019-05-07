#!/usr/bin/env python3
# Typeset the run into correct format 
# Stephan Kuschel, Matt Ware, Catherine Saladrigas, 2019

import sys

def runFormat( runNumber ):
    return '/r{0:04d}'.format(int(runNumber))

print(runFormat( sys.argv[1] ))
