# import the package
import sqs_nqs_tools as nqs
print("package import success")

# import the modules
from sqs_nqs_tools.helper import *
from sqs_nqs_tools.generatorpipeline import *
from sqs_nqs_tools.dataaccess import *
from sqs_nqs_tools.tof import *
from sqs_nqs_tools.MCP import *
from sqs_nqs_tools.offlineAccess import *
from sqs_nqs_tools.clustersize import *
from sqs_nqs_tools.correlationPlots import *
from sqs_nqs_tools import analysis
print("module import success")

# print the version
print("Version of sqs_nqs_tools : "+nqs.__version__)




print("done testing")


