import numpy as np
import matplotlib.pyplot as plt
import karabo_bridge as kb
import karabo_data as kd

runDataDict = dict()
runDataDict["runDir"]=None
runDataDict["runData"]=None

raw_dir = '/gpfs/exfel/exp/SQS/201802/p002195/raw/'

def runFormat( runNumber ):
    '''
    formats run number for accessing data through karabo commands
        inputs 
            runNumber = run of interest
        outputs
            returns formatted run number   
    '''
    return '/r{0:04d}'.format(runNumber)

def runDir( runNumber , path=raw_dir):
    '''
    formats run number to path where hdf5 files are located -> for accessing data through karabo commands
        inputs 
            runNumber = run of interest
            optional path = path where all the runs are located - default: raw directory
        outputs
            returns runDirectory as string
    '''
    runStr = runFormat( runNumber )
    runDirectory = path+runStr
    return runDirectory

def getData(runDir, devicePath, dataPath, forceUpdate = False):
    '''
        Returns Data from given adress / device using Karabo Data or using already loaded data if no update forced and run already loaded
        run_dir - directory of run files (hdf5)
        device_path - path for device in hdf5 file eg "SQS_AQS_MOV/MOTOR/Y_DOWNSTR"
        data_path - path to data within hdf5 device path eg "actualPosition.value"
    '''
    if runDataDict["runDir"] is not None and runDataDict["runData"] is not None and not forceUpdate and runDataDict["runDir"] == runDir:
        # no action needed the dictionary runDataDict contains already the data we are interested in and user does not neccesarily desires the update
        pass
    else:
        runDataDict["runData"] = kd.RunDirectory(runDir)
        runDataDict["runDir"] = runDir
        
    data = runDataDict["runData"].get_array(devicePath, dataPath)
    
    return data

def getTrainIds( runDir , forceUpdate = False):
    '''
    Gets train IDs of specified run
        inputs 
            runNumber = number of run of interest
            path = path for data; defined at the top
        outputs
            array of train IDs 

    '''
    if runDataDict["runDir"] is not None and runDataDict["runData"] is not None and not forceUpdate and runDataDict["runDir"] == runDir:
        # no action needed the dictionary runDataDict contains already the data we are interested in and user does not neccesarily desires the update
        pass
    else:
        runDataDict["runData"] = kd.RunDirectory(runDir)
        runDataDict["runDir"] = runDir
        
    return runDataDict["runData"].train_ids
    
def allAvailableDataSources( runDir , forceUpdate = False):
    if runDataDict["runDir"] is not None and runDataDict["runData"] is not None and not forceUpdate and runDataDict["runDir"] == runDir:
        # no action needed the dictionary runDataDict contains already the data we are interested in and user does not neccesarily desires the update
        pass
    else:
        runDataDict["runData"] = kd.RunDirectory(runDir)
        runDataDict["runDir"] = runDir
    return runDataDict["runData"].all_sources
