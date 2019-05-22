import numpy as np
from matplotlib import pylab as plt
from scipy.optimize import curve_fit
import time
# Import karabo libraries
import karabo_bridge as kb
import karabo_data as kd
import sqs_nqs_tools as xfel

''' 
Radially integrates a scattering image

    inputs:
        data = 2D scattering image
        center = np.array([x,y]), center of the image
    outputs: 
        radialprofile = 1D radially integrated array
'''

def radial_profile(data,center):
    y,x = np.indices((data.shape))
    r = np.sqrt( (x-center[0])**2 + (y-center[1])**2 )
    r = r.astype((np.int))
    
    tbin = np.bincount(r.ravel(), data.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    return radialprofile

'''
Calculates atomic form factor for Carbon

    inputs:
        q = |Q|, momentum transfer, takes an array of values
    output:
        f = formfactor, returns an array
'''

def formfactor(q):
# for Carbon
    a = np.array([2.31, 1.02, 1.5886,0.865])
    b = np.array([20.8439,10.2075,0.5687,51.6512])
    c = 0.2156
    
# for Neon
#   a = np.array([3.9553, 3.1125, 1.4546, 1.1251])
#   b = np.array([8.4042, 3.4262, 0.2306, 21.7184])
#   c = 0.3515

    f= np.zeros(len(q))+c
    for idx in range(len(a)):
        ai=a[idx]
        bi=b[idx]
        f += ai*np.exp(-bi*(q/(4*np.pi))**2)       
    return f

'''
Scattering intensity for radially integrated images

    inputs: 
        q = |Q|, momentum transfer, takes an array of values
        a = amplitude
        r = cluster size
    outputs:
        returns scattering intensity
'''

def scatFunc(q,a,r):
    return a*(np.sinc(r*q)+ 1)*(formfactor(q))**2

'''
fitting scattering intensity function to a radially integrated image

    input:
        x_data = right now this is pixel number.  Needs to be callibrated for q
        y_data = radially integrated intensity from scattering image
    output: 
        popt = [amplitude, cluster size]
'''

def clusterFit(x_data, y_data):
    #for radially integrated data
    popt, pcov = curve_fit(scatFunc, x_data, y_data)
    return popt
    #return popt[1]

'''
This function calculates the size of a cluster, given an scattering image

    input:
        image = scattering image to be analyzed
        center = np.array([x,y]), center of the image
    output:
        clustersize = size of the cluster (currently not callibrated)
'''

#returns cluster size
#removes center of image (currently set to get rid of first 10 points)

def clusterSize (image, center):
    intensity = radial_profile(image, center)
    intCrop = intensity[10:]
    pixel = np.arange(0, len(intCrop))
    popt = clusterFit(pixel, intCrop)
    clustersize = popt[1]
    return clustersize


