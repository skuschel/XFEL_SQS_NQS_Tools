function out = read_xgm(info)
    filename = sprintf('RAW-R%04d-DA02-S00000', info.run);
    path_full = sprintf('%s/%s.h5', info.path, filename);

    XGM_energy      = '/CONTROL/SA3_XTD10_XGM/XGM/DOOCS/pulseEnergy/photonFlux/value';
    XGM_intensity   = '/INSTRUMENT/SA3_XTD10_XGM/XGM/DOOCS:output/data/intensityTD';
    XGM_trainId     = '/INSTRUMENT/SA3_XTD10_XGM/XGM/DOOCS:output/data/trainId';
    
    out.energy      = h5read(path_full, XGM_energy);
    out.intensity   = h5read(path_full, XGM_intensity);
    out.trainId     = h5read(path_full, XGM_trainId);
end