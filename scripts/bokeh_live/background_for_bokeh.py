import sqs_nqs_tools as nqs
from sqs_nqs_tools.offline import access, adata, tof

# Plot options
import matplotlib.pyplot as plt

# Import required libraries
import numpy as np 
import pyqtgraph as pg

# Import karabo libraries
import karabo_bridge as kb
import karabo_data as kd

def print_stats(arr):
    print(np.max(np.asarray(arr)))
    print(np.min(np.asarray(arr)))
    print(np.mean(np.asarray(arr)))
    print('---')

for_sean = False
dark_only = False
run_bg = 368
run_dark = 365
raw_path ='/gpfs/exfel/exp/SQS/201802/p002195/raw'
outpath_sean = '/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_for_recreation/'
if not dark_only:
    pnCCDdata = adata.getPnCCD(run_bg,path=raw_path)
pnCCDdata_dark = adata.getPnCCD(run_dark,path=raw_path)

#~ print(pnCCDdata.shape)

if not dark_only:
    dark_avg = np.mean(pnCCDdata_dark.sel(trainId=slice(10,1e10)),axis=0)
    dark_avg_2 = np.asarray(dark_avg.copy())
    dark_avg_2[dark_avg_2<0] = 0
    
    pnCCDdata_p = pnCCDdata.copy()
    pnCCDdata_p = np.asarray(pnCCDdata_p)-dark_avg_2
    #~ for i in range(pnCCDdata.shape[0]):
        #~ pnCCDdata_p[i,:,:] = pnCCDdata_p[i,:,:] - dark_avg_2
        #~ if False:
            #~ cm_mode_avgs_upper = np.mean(pnCCDdata_p[i,0:150,:], axis = 0)
            #~ cm_mode_cor_upper = np.matlib.repmat(np.squeeze(cm_mode_avgs_upper),512,1)
            #~ cm_mode_avgs_lower = np.mean(pnCCDdata_p[i,(1023-150):1023,:], axis = 0)
            #~ cm_mode_cor_lower = np.matlib.repmat(np.squeeze(cm_mode_avgs_lower),512,1)
            #~ print(cm_mode_avgs_lower.shape)
            #~ print(cm_mode_cor_lower.shape)
            #~ cm_mode_cor = np.concatenate((cm_mode_cor_upper,cm_mode_cor_lower))
            #~ pnCCDdata_p[i,:,:] = pnCCDdata_p[i,:,:] - cm_mode_cor
    pnCCDmax =  np.max(pnCCDdata_p,axis=0)
    pnCCDavg = np.mean(pnCCDdata.sel(trainId=slice(10,1e10)),axis=0)-dark_avg
    print_stats(np.mean(pnCCDdata.sel(trainId=slice(10,1e10)),axis=0))
else:
    pnCCDavg = np.mean(pnCCDdata_dark,axis=0)
pnCCDavg = np.squeeze(pnCCDavg)

print_stats(np.mean(pnCCDdata_dark.sel(trainId=slice(10,1e10)),axis=0))
print_stats(pnCCDavg)
print_stats(pnCCDmax)
#~ pnCCDavg = np.mean(pnCCDdata_dark.sel(trainId=slice(10,1e10)),axis=0)
if for_sean:
    fname = "background_for_substraction_r"+str(run_bg)+"_darkR"+str(run_dark)+".dat"
    np.savetxt(outpath_sean+fname,pnCCDavg,delimiter=",")
else:
    if not dark_only:
        np.save('background_pnCCD.npy',pnCCDavg)
        np.save('background_max_pnCCD.npy',pnCCDmax)
    else:
        np.save('dark_pnCCD.npy',pnCCDavg)
