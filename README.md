
# README

This repository contains a collection of functions and tools for live analysis.

Issue tracker and main repo: https://github.com/skuschel/XFELMay2019/issues


# How to use this repo

1) load python modules via before running any program:
  `module load anaconda3/5.2`

2) Every program should be executable and displays a helptext explaining the arguments when run with `-h`. Example: `./toflive.py -h`

# Code in this repo
## toflive.py
Run as 
'''bash
python toflive.py datahost (optional)
'''

Plots live images of the TOF, including running average.


