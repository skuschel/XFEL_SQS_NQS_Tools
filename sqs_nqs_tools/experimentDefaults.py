#file to define the settings. We can make this load from a config file later

# Load experiment config dict into module wide variable
defaultConf = dict()

#Define the defaults for DataStream
defaultConf['dataStream_tcp_offline'] = "tcp://127.0.0.1:8010" # for argument "offline"
defaultConf['dataStream_tcp_live'] = "tcp://10.253.0.142:6666" # for argument "live"
defaultConf['dataStream_tcp_default'] = "tcp://10.253.0.142:6666" # for no argument given | makes scripts without input arguments run in live mode by default

#Define important Directories:
defaultConf['rawDir'] = '/gpfs/exfel/exp/SQS/201802/p002195/raw' # directory with raw files

#Define the defaults for all the detector settings
defaultConf['tofRange'] = [142000,600000] #the range where interesting data appears 142000
defaultConf['tofBaseEnd'] = 5000 # the first n samples to consider as baseline
defaultConf['tofChannels'] = 16 #the number of simultaneous channels in the Tof

#device addresses
#~ defaultConf['imageDevice'] = 'SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput' # MCP
defaultConf['imageDevice'] = 'SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output' # calibrated pnCCD
defaultConf['imageDeviceElement'] = 'data.image'
defaultConf['tofDevice'] = 'SQS_DIGITIZER_UTC1/ADC/1:network'
defaultConf['tofDeviceElement'] = 'digitizers.channel_1_A.raw.samples'
defaultConf['pulseEDevice'] = 'SA3_XTD10_XGM/XGM/DOOCS'

#multiprocessing settings
defaultConf['dataWorkers'] = 4
