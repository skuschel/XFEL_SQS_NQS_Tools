function out = read_pnccd(info)
    files = get_files(info.path, 'PNCCD01');
    
    out.data = [];
    out.trainId = [];
    
    for i=1:numel(files)
        path_full = sprintf('%s/%s', files(i).folder, files(i).name);

        pnccd_image     = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image';
        pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';
    
        out.data   = cat(3, out.data, h5read(path_full, pnccd_image));
        out.trainId = [out.trainId; h5read(path_full, pnccd_trainId)];
    end
end


