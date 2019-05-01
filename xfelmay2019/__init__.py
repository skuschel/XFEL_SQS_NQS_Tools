'''
The python package initally developed for the data analysis on the
EuropeanXFEL in Hamburg in May 2019.

see https://github.com/skuschel/XFELMay2019
'''

from .helper import *
from .generatorpipeline import *
from .dataaccess import *
from .tof_offline import *
from . import analysis


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

print('Welcome to xfelmay2019 version {}'.format(__version__))
