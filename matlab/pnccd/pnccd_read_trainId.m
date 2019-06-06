function out = pnccd_read_trainIds(info)
    files = get_files(info.path, 'PNCCD01');

    out.trainId = [];
    out.fileNr = [];
    out.pic_idx= [];

    for i=1:numel(files)
        path_full = sprintf('%s/%s', files(i).folder, files(i).name);

        pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';

        tid = h5read(path_full, pnccd_trainId);
        
        out.trainId = [out.trainId; tid];
        out.fileNr  = [out.fileNr; ones(size(tid))*i];
        out.pic_idx = [out.pic_idx; (1:numel(tid))'];
    end
end
