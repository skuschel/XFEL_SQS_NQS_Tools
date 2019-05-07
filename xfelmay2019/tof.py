import numpy as np
import matplotlib.pyplot as plt
import karabo_bridge as kb
import karabo_data as kd


def averageTOF( tofs ):
    '''
    takes TOF data for a given run and averages.  
        inputs
            tofs = array of all tof data from a given run
        outputs
            an array of the averaged tof spectra  
    '''
    return np.mean( tofs, 0 )

def runFormat( runNumber ):
    '''
    formats run number for accessing data through karabo commands
        inputs 
            runNumber = run of interest
        outputs
            returns formatted run number   
    '''
    return '/r{0:04d}'.format(runNumber)

def plotTOF( pixels, tof, xlabel='pixels' ):
    '''
    Plots TOF spectra, not callibrated for m/z 
        inputs 
            pixels = uncallibrated time of flight x-axis
            tof = array of a single TOF spectra
        outputs
            plot of tof data   
    '''
    plt.plot( pixels, tof )
    plt.ylim( 0, np.min(tof) )
    plt.xlabel( xlabel )
    plt.ylabel( 'TOF ' )

def plotVerticalLine( xpos, scale = 1e6, color='k', label=None ):
    '''
    Plots vetical line that will be used to identify ROI
        inputs 
            xpos = position of vertical line 
        outputs
            plots vertical line
    '''
    if label is None:
        plt.plot( [xpos,xpos],np.array([-1,1])*scale, color )
    else:
        plt.plot( [xpos,xpos],np.array([-1,1])*scale, color, label=label )


def showROIs( pixels, tof, onePlus, lightPeak, highCharge ):
    '''
    used to overlay vertical  lines defining ROI's on TOF spectra
        inputs 
            pixels= uncallibrated time of flight x-axis
            tof = array of a single TOF spectra
            onePlus = array specificing range of TOF spectra considered for X+
            lightPeak = array specificing range of TOF spectra considered for light peak
            highCharge = array specificing range of TOF spectra considered for X(n+)
        outputs
            Plot of specified TOF spectra, with ROI's marked
    ''' 
    plt.figure( figsize=(10,5) )
    plotTOF(pixels , tof )

    onePlusLeft = onePlus[0]
    onePlusRight = onePlus[1]
    plotVerticalLine( onePlusLeft, color='g', label='1+' )
    plotVerticalLine( onePlusRight, color='g' )

    lightPeakLeft = lightPeak[0]
    lightPeakRight = lightPeak[1]
    plotVerticalLine( lightPeakLeft, color='r', label='Light peak' )
    plotVerticalLine( lightPeakRight, color='r' )

    highChargeLeft = highCharge[0]
    highChargeRight = highCharge[1]
    plotVerticalLine( highChargeLeft, color='k', label='High charge states' )
    plotVerticalLine( highChargeRight, color='k' )

    plt.legend(  ) 


def averageBrightestTOFs( pixels, tofs, integrateAt=(280000 - 1000,280000 + 1500), behlkeAt=268000 ):
    '''
    Averages the brightest TOFs from a given run, ie outlier rejection
        inputs 
            pixels = uncallibrated time of flight x-axis
            tofs = array of all tof data from a given run
        outputs
            a 1D array of the averaged brightest TOFs
    '''  
    fullSum = np.abs(np.sum( tofs[:,(behlkeAt<pixels)], 1 ))
    onePlusSum = np.nansum( tofs[:, (integrateAt[0]<pixels)&(pixels<integrateAt[1]) ], 1 )
    
    maxSum = np.max((fullSum))
    interestingShots = fullSum > maxSum*.5
    
    ratio = np.abs(onePlusSum.astype(float))[interestingShots]
    
    maxRatio = np.max(ratio)
    
    subtofs=tofs[interestingShots,:]
    return np.mean(subtofs[ratio > maxRatio*.8,:], 0)
    
      
def waterfallTOFs( pixels, tofs, labels=None, figsize=(10,5), waterfallDelta=None):  
    '''
    Plots all TOFs of a given run in a waterfall plot
        inputs 
            pixels= uncallibrated time of flight x-axis
            tofs=array of all tof data from a given run
        outputs
            waterfall plot, sans labels unless otherwise specified
    '''
    plt.figure(figsize=figsize)
    offset = 0.
    if labels is None:
        for tof in tofs:
            plt.plot( pixels , tof + offset )
            if waterfallDelta is None:
                offset += np.min( tof )
            else:
                offset += waterfallDelta
    else:
        startTextX = pixels[-1] - 2e3
        for tof, label in zip(tofs,labels):
            plt.plot( pixels , tof + offset, label=label )
            baseline = tof[0]+offset + 40        
            plt.annotate(label, (startTextX, baseline))
            if waterfallDelta is None:
                offset += np.min( tof )
            else:
                offset += waterfallDelta
        
        
def overlayTOFs( pixels, tofs, labels=None):  
    '''
    Plots all TOFs of a given run, overlayed 
        inputs 
            pixels= uncallibrated time of flight x-axis
            tofs=array of all tof data from a given run
        outputs
            plot of specified tof spectra, sans labels unless otherwise specified

    '''
    plt.figure(figsize=(10,5))
    if labels is None:
        for tof in tofs:
            plt.plot( pixels , tof, alpha=0.5 )
    else:
        for tof, label in zip(tofs,labels):
            plt.plot( pixels , tof, label=label, alpha=0.5 )
        plt.legend()


def getRunTOF( runNumber, path, tofrange=(260000,285000), 
              dirspec='SQS_DIGITIZER_UTC1/ADC/1:network', 
              elementspec='digitizers.channel_1_A.raw.samples' ):
    '''
    gets TOF data for a given run 
        inputs 
            runNumber = number of run of interest
            path = path for data; defined at the top
        outputs
            pixels = 
            tofdata 
            trainIds

    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    pixels = np.arange(tofrange[0],tofrange[1])
    
    data = runData.get_array( dirspec,elementspec )
    tofdata=np.asarray(data)[ : , tofrange[0]:tofrange[1] ]
    trainIds =np.asarray(data.trainId)
    return pixels, tofdata, trainIds  

def getTrainIds( runNumber, path ):
    '''
    Gets train IDs of specified run
        inputs 
            runNumber = number of run of interest
            path = path for data; defined at the top
        outputs
            array of train IDs 

    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    return runData.train_ids

def waterfallBrightest( pixels, tofs, nbright=100, 
                                      threshSum=0.1, behlkeAt=268000,
                                      integrateAt=(269000 - 200, 276000)):  
    '''
    Makes waterfall plot of the brightest TOF spectra from a given run, labeled with train ID
    Can be sorted by onePlus, lightPeak, or highCharge (defined at the top) by specifying onePlus =
        inputs
            pixels= uncallibrated time of flight x-axis
            tofs=array of all tof data from a given run
            trainIds = array of train IDs from a run
        displays
            waterfall plot
    '''
    plt.figure(figsize=(10,100))
    offset = 0.
    
    fullSum = np.abs(np.sum( tofs[:,(behlkeAt<pixels)], 1 ))
    
    maxSum = np.max((fullSum))
    interestingShots = fullSum > maxSum*threshSum
    
    onePlusSum = np.nansum( tofs[:, (integrateAt[0]<pixels)&(pixels<integrateAt[1]) ], 1 )
    
    ratio = np.abs(onePlusSum.astype(float) )[interestingShots]
    
    inds = np.argsort(ratio)[-nbright:]
    
    subtofs = tofs[interestingShots,:]
    
    for idx, currind in enumerate(inds):
        tof = subtofs[currind,:]
        plt.plot( pixels[behlkeAt<pixels] , tof[behlkeAt<pixels] + offset )
        offset += np.min( tof[behlkeAt<pixels] )
        
        
def waterfallBrightest_labelByTrainId( pixels, tofs, trainIds, nbright=100, 
                                      threshSum=0.1, behlkeAt=268000,
                                      integrateAt=(269000 - 200, 276000)):  
    '''
    Makes waterfall plot of the brightest TOF spectra from a given run, labeled with train ID
    Can be sorted by onePlus, lightPeak, or highCharge (defined at the top) by specifying onePlus =
        inputs
            pixels= uncallibrated time of flight x-axis
            tofs=array of all tof data from a given run
            trainIds = array of train IDs from a run
        displays
            waterfall plot, w/ TIDs labeled
        outputs
            trainIDs of brightest shots
    '''
    plt.figure(figsize=(10,100))
    offset = 0.
    
    fullSum = np.abs(np.sum( tofs[:,(behlkeAt<pixels)], 1 ))
    
    maxSum = np.max((fullSum))
    interestingShots = fullSum > maxSum*threshSum
    
    onePlusSum = np.nansum( tofs[:, (integrateAt[0]<pixels)&(pixels<integrateAt[1]) ], 1 )
    
    ratio = np.abs(onePlusSum.astype(float) )[interestingShots]
    
    inds = np.argsort(ratio)[-nbright:]
    
    subtofs = tofs[interestingShots,:]
    subtrains = trainIds[interestingShots]
    
    startTextX = pixels[-1] - 2e3
    
    for idx, currind in enumerate(inds):
        tof = subtofs[currind,:]
        plt.plot( pixels[behlkeAt<pixels] , tof[behlkeAt<pixels] + offset )
        
        baseline = tof[0]+offset + 40
        
        
        plt.annotate(str( subtrains[ currind ] ), (startTextX, baseline))
        offset += np.min( tof[behlkeAt<pixels] )
        
    return subtrains[inds]

def getAvgRunsTOF( runRange, path, tofrange ):
    NR = runRange.size

    tofs=[]
    for ir,arun in enumerate(runRange):
        pixels, tof, tids = getRunTOF( arun, path, tofrange=tofrange)
        avgtof = averageTOF(tof)
        tofs.append(avgtof)
        
    return tofs

def getBrightAvgRunsTOF( runRange, path, tofrange, integrateAt =(280000 - 1000,280000 + 1500), behlkeAt=268000):
    NR = runRange.size

    tofs=[]
    for ir,arun in enumerate(runRange):
        pixels, tof, tids = getRunTOF( arun, path, tofrange=tofrange)
        avgtof = averageBrightestTOFs( pixels, tof, integrateAt=integrateAt, behlkeAt=behlkeAt )
        tofs.append(avgtof)
        
    return tofs


################ OLD TOF FUNCS #############33
def tofAverager( runData, nmax = 50 ):
    '''
    generates average of tofdata across nmax shots
    input:
        runData: run directory generated from karabo_data.RunDirectory(path+run)
        nmax: number of tof traces to average over from run
    output:
        averaged tof trace (np.array, float)
    '''
    tofsum = None
    isum = 0
    for tid, data in runData.trains():
    #     print("Processing train", tid)
        tofdata = data['SQS_DIGITIZER_UTC1/ADC/1:network']['digitizers.channel_1_A.raw.samples']
        if tofsum is None:
            tofsum = tofdata
            isum += 1
        else:
            tofsum += tofdata
            isum += 1
        if isum > nmax:
            break
    return tofsum/float(nmax)

def normalizedTOF( toftrace , downsampleRange=(268000,280000) , baselineFrom=-2000 ):
    '''
    input:
        toftrace: raw tof trace
        downsampleRange: (int,int) tuple giving range over which to downsmaple TOF
        baselineFrom: gives start index for calculating baseline average
    output:
        normalizedTOFTrace: puts tof trace in standard form for analysis
    '''
    # Reduce dimension of TOF to span desired range
    newtof = toftrace[downsampleRange[0]:downsampleRange[1]]
    N = newtof.size
    x = np.arange(N)

    # Substract mean of remaining TOF trace and take absolute value
    newtof_mean = np.mean( newtof[baselineFrom:] )
    return np.abs(newtof - newtof_mean)

from scipy.signal import find_peaks_cwt
def findTOFPeaks( toftrace ):
    '''
    input:
        toftrace: use normalized tof trace generated from normalizedTOF, numpy array of floats
    output:
        peak_positions: returns indexes of the TOF peaks
        peak_values: returns height of TOF peaks
    '''
    base_width = 200.
    # Find indexes of inds
    zf = find_peaks_cwt(toftrace, [base_width, base_width/2., base_width/4.])
    
    # Create averaging zones around peaks
    zguess = np.zeros_like(zf).astype(float) # allocate space

    for ii,zfi in enumerate(zf):
        xlow = (np.round( zfi - base_width/2. )).astype(int)
        if xlow < 0:
            xlow = 0
        xhigh = (np.round( zfi + base_width/2. )).astype(int)
        if xhigh > toftrace.size:
            xhigh = toftrace.size
            
        zguess[ii] = np.max(toftrace[xlow:xhigh])
        
    return zf, zguess





