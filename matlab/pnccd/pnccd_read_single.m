function out = pnccd_read_single(path, trainId)
    tic;
    out = pnccd_read_trainId(path);
    toc;
    
    trainId_list = out.trainId;
    fileNr_list = out.fileNr;
    pic_idx = cast(out.pic_idx, 'double');
    
    idx = find(trainId==trainId_list);
    
    disp(idx);
    

    files = get_files(path, 'PNCCD01');


    i = fileNr_list(idx);
    
    fprintf('Loading pnccd file %02d/%02d\n', i, numel(files));
    path_full = sprintf('%s/%s', files(i).folder, files(i).name);

    pnccd_image     = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image';
    pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';

    out.data    = h5read(path_full, pnccd_image, [1,1,pic_idx(idx)], [1024,1024,1]);
    out.trainId = h5read(path_full, pnccd_trainId, pic_idx(idx), 1);

    out.data = cast(out.data, 'double');
end


