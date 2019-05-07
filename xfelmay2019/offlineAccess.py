import numpy as np
import matplotlib.pyplot as plt
import karabo_bridge as kb
import karabo_data as kd


def runFormat( runNumber ):
    '''
    formats run number for accessing data through karabo commands
        inputs 
            runNumber = run of interest
        outputs
            returns formatted run number   
    '''
    return '/r{0:04d}'.format(runNumber)


def getPulseEnergies( run , path ):
    '''
        Returns pulse energy
        BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.
    '''
    runStr = runFormat( run )
    runData = kd.RunDirectory(path+runStr)
    print('BE WARY OF THIS FUNCTION!!!! Might not return true PE depending on train settings.')
    data = runData.get_array( 'SA3_XTD10_XGM/XGM/DOOCS:output','data.intensityTD')
    return np.asarray(data.trainId), np.asarray(data[:,120])

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