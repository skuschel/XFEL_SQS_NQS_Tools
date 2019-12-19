##*** seems more like an offline analysis script - strip out the analysis functions and then make a seperate offline loader?

import numpy as np
import matplotlib.pyplot as plt
import karabo_bridge as kb
import karabo_data as kd


def runFormat( runNumber ): ##*** should this be in here?
    '''
    formats run number for accessing data through karabo commands
        inputs 
            runNumber = run of interest
        outputs
            returns formatted run number   
    '''
    return '/r{0:04d}'.format(runNumber)



def analyzeAverageImage( runNumber, 
                        path='/gpfs/exfel/exp/SQS/201921/p002430/raw', ###imagePath
                        maskRadius=100):
    '''
    finds mean scattering and plots and returns that image
    input:
        runNumber: to analyze
        path: to experiment H5s
        maskRadius: radius below which to ignore for determining max scattering
        saveDir: path to save picture to
    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    trainIds = runData.train_ids
    
    scatImages = np.asarray(runData.get_array('SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', 'data.image.pixels'))
    scatMean = np.mean(scatImages,0).astype(float)
    
    return scatMean


def allImages( runNumber, path='/gpfs/exfel/exp/SQS/201921/p002430/raw'):
    '''
    finds mean scattering and plots and returns that image
    input:
        runNumber: to analyze
        path: to experiment H5s
    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    trainIds = runData.train_ids
    
    scatImages = np.asarray(runData.get_array('SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', 'data.image.pixels'))
    
    return scatImages, trainIds


def analyzeMaximumImage( runNumber, 
                        path='/gpfs/exfel/exp/SQS/201921/p002430/raw',
                        maskRadius=100):
    '''
    finds maximum scattering and plots that image
    input:
        runNumber: to analyze
        path: to experiment H5s
        maskRadius: radius below which to ignore for determining max scattering
        saveDir: path to save picture to
    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    trainIds = runData.train_ids
    
    scatImages = np.asarray(runData.get_array('SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', 'data.image.pixels'))

    NT,NX,NY = scatImages.shape
    xs = np.arange(NX)
    ys = np.arange(NY)
    YY,XX = np.meshgrid( ys , xs )
    RR = np.sqrt( ( XX - NX/2. )**2 + ( YY - NY/2. )**2 )
    MASK = RR < maskRadius
    
    maskedScats = np.copy(scatImages)
    maskedScats[:,MASK] = 0.
    
    scaledScat = np.sum( maskedScats, (1,2) ) 
    
    indMax = np.argmax(scaledScat)
    indMin = np.argmin(scaledScat)

    scatMax = scatImages[indMax,:,:].astype(float)
    scatMean = np.mean(scatImages,0).astype(float)
    
    plt.figure(5)
    plt.imshow(scatMax)
    plt.title( 'Max scattering from run %d' % runNumber )
    plt.colorbar()
    plt.show()
    plt.pause(2)
    
    plt.figure(5)
    plt.imshow( np.log(np.abs(scatMax/np.sum(scatMax.flatten()) -   scatMean/np.sum(scatMean.flatten())))  )
    plt.title( 'Log of difference between scatMax/intensity-scatMean/intensity from run %d' % runNumber )
    plt.colorbar()
    plt.show()
    plt.pause(2)
    
    plt.figure(5)
    plt.imshow( scatMean  )
    plt.title( 'Mean from run %d' % runNumber )
    plt.colorbar()
    plt.show()
    plt.pause(2)
    
    del scatImages
    del maskedScats
    
    return scatMax, trainIds[indMax]

def analyzeMaximumImages( runNumber, 
                        path='/gpfs/exfel/exp/SQS/201921/p002430/raw',
                        maskRadius=100,
                        nlargest=10):
    '''
    finds maximum scattering images and plots that image, saving to saveDir
    input:
        runNumber: to analyze
        path: to experiment H5s
        maskRadius: radius below which to ignore for determining max scattering
        nlargest: number of largest images to plot
    '''
    run = runFormat( runNumber )
    runData = kd.RunDirectory(path+run)
    trainIds = runData.train_ids
    
    scatImages = np.asarray(runData.get_array('SQS_DPU_LIC/CAM/YAG_UPSTR:daqOutput', 'data.image.pixels'))

    NT,NX,NY = scatImages.shape
    xs = np.arange(NX)
    ys = np.arange(NY)
    YY,XX = np.meshgrid( ys , xs )
    RR = np.sqrt( ( XX - NX/2. )**2 + ( YY - NY/2. )**2 )
    MASK = RR < maskRadius
    
    maskedScats = np.copy(scatImages)
    maskedScats[:,MASK] = 0.
    
    scaledScat = np.sum( maskedScats, (1,2) ) 
    indMaxToMin = np.argsort( scaledScat )[-nlargest:]
    
    fig, axes = plt.subplots(nlargest, 1, figsize=(10,100))
    
    for idx,ax in enumerate(axes):
        realInd = indMaxToMin[idx]
        plotme=scatImages[realInd,:,:].squeeze()
        im=ax.imshow( plotme.astype(float) )
        ax.set_title('run %d and tid %d' % (runNumber, trainIds[realInd]))

    plt.show()
    plt.pause(2)
    
    
    del scatImages
    del maskedScats
    
    
def plotWithCircularMask( image, maskRadius ):
    NX,NY =  image.shape
    xs = np.arange(NX)
    ys = np.arange(NY)
    YY,XX = np.meshgrid( ys , xs )
    RR = np.sqrt( ( XX - NX/2. )**2 + ( YY - NY/2. )**2 )
    MASK = RR < maskRadius
    
    maskedScats = np.copy( image )
    maskedScats[MASK] = 0.
    
    plt.figure(figsize=(10,10))
    plt.imshow(maskedScats)
    
def histWithCircularMask( image, maskRadius, nbins=1000 ):
    NX,NY =  image.shape
    xs = np.arange(NX)
    ys = np.arange(NY)
    YY,XX = np.meshgrid( ys , xs )
    RR = np.sqrt( ( XX - NX/2. )**2 + ( YY - NY/2. )**2 )
    MASK = RR < maskRadius
    
    maskedScats = np.copy( image )
    maskedScats[MASK] = 0.
    
    plt.figure(figsize=(10,3))
    plt.hist(maskedScats.flatten(), bins=nbins)
