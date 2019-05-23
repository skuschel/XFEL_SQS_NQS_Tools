'''
The python package initally developed for the data analysis on the
EuropeanXFEL in Hamburg in May 2019.

see https://github.com/skuschel/XFELMay2019
'''

from sqs_nqs_tools.helper import *
from .generatorpipeline import *
from .dataaccess import *
from .bufferPlots import *
from .sourceParser import *
#from .tof import *
#from .MCP import *
#from .offlineAccess import *
#from .clustersize import *
#from .correlationPlots import *
from .experimentDefaults import *
#from . import analysis


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


# Done -> Welcome Message

print('Welcome to sqs_nqs_tools.online version {}'.format(__version__))
