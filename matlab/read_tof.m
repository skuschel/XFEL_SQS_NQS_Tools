function out = read_tof(info)
    files = get_files(info.path, 'DA02');
    
    for i=1:1%numel(files)
        path_full = sprintf('%s/%s', files(i).folder, files(i).name);

        TOF_data          = '/INSTRUMENT/SQS_DIGITIZER_UTC1/ADC/1:network/digitizers/channel_1_A/raw/samples';
        TOF_trainId  = '/INSTRUMENT/SQS_DIGITIZER_UTC1/ADC/1:network/digitizers/trainId';
    
        out.data   = h5read(path_full, TOF_data );
        out.trainId = h5read(path_full, TOF_trainId);
    end
end