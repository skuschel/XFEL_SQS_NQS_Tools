'''
The python package initally developed for the data analysis on the
EuropeanXFEL in Hamburg in May 2019.

see https://github.com/skuschel/XFELMay2019
'''

from .helper import *
from .generatorpipeline import *
from .dataaccess import *
from .tof import *
from .MCP import *
from .offlineAccess import *
from .clustersize import *
from .correlationPlots import *
from . import analysis


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# Load experiment config dict into module wide variable

import json
config_dict = dict()
with open('exp_config.json','r') as f:
	config_dict = json.load(f)

# Done -> Welcome Message

print('Welcome to sqs_nqs_tools version {}'.format(__version__))
