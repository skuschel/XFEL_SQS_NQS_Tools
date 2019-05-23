import numpy as np
import matplotlib.pyplot as plt
import karabo_bridge as kb
import karabo_data as kd

runDataDict = dict()
runDataDict["runDir"]=None
runDataDict["runData"]=None

def runFormat( runNumber ):
    '''
    formats run number for accessing data through karabo commands
        inputs 
            runNumber = run of interest
        outputs
            returns formatted run number   
    '''
    return '/r{0:04d}'.format(runNumber)
    


def getData(runDir, devicePath, dataPath, forceUpdate = False):
	'''
        Returns Data from given adress / device using Karabo Data or using already loaded data if no update forced and run already loaded
        run_dir - directory of run files (hdf5)
        device_path - path for device in hdf5 file eg "SQS_AQS_MOV/MOTOR/Y_DOWNSTR"
        data_path - path to data within hdf5 device path eg "actualPosition.value"
    '''
    global runDataDict
    
    if runDataDict["runDir"] is not None and runDataDict["runData"] is not None and not forceUpdate and runDataDict["runDir"] == runDir:
		# no action needed the dictionary runDataDict contains already the data we are interested in and user does not neccesarily desires the update
		pass
	else:
		runDataDict["runData"] = kd.RunDirectory(runDir)
		runDataDict["runDir"] = runDir
		
    data = runDataDict["runData"].get_array(devicePath, dataPath)
    
    return data
	
	

def getPulseEnergies( run , path ):
    '''
        Returns pulse energy
        BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.
    '''
    runStr = runFormat( run )
    runData = kd.RunDirectory(path+runStr)
    print('BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.')
    data = runData.get_array( 'SA3_XTD10_XGM/XGM/DOOCS:output','data.intensityTD')
    dataArray = np.asarray( data )
    PID = np.argmin( np.abs( dataArray[0,:]-1 ) )
    
    
    return np.asarray(data.trainId), np.asarray(data[:,PID-1])

def getChamberHeight( run , path ):
    runStr = runFormat( run )
    runData = kd.RunDirectory(path+runStr)
    data=(runData.get_array( 'SQS_AQS_MOV/MOTOR/Y_DOWNSTR','actualPosition.value'))    
    return np.asarray(data.trainId), np.asarray(data)
    
def getPulseDelay( run , path ):
    runStr = runFormat( run )
    runData = kd.RunDirectory(path+runStr)
    data=(runData.get_array( 'SQS_NQS_CRSC/TSYS/PARKER_TRIGGER','actualDelay.value'))   
    return np.asarray(data.trainId), np.asarray(data)
