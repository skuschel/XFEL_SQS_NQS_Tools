function out = pnccd_read_all(info, varargin)
    files = get_files(info.path, 'PNCCD01');

    out.data = [];
    out.trainId = [];

    tic;
    for i=1:numel(files)
        if nargin>1
            files_in = varargin{1};
            if sum(files_in==i)==0
               continue; 
            end
        end
        
        fprintf('Loading pnccd file %02d/%02d\n', i, numel(files));
        path_full = sprintf('%s/%s', files(i).folder, files(i).name);

        pnccd_image     = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image';
        pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';

        out.data   = cat(3, out.data, h5read(path_full, pnccd_image));
        out.trainId = [out.trainId; h5read(path_full, pnccd_trainId)];
    end
    toc;

    fprintf('Casting images to double...\n');
    tic;
    out.data = cast(out.data, 'double');
    toc;
    
    out.sum  = squeeze(sum(sum(out.data, 1), 2));


    fprintf('Removing empty images...\n');
    tic;
    out.data(:,:, out.sum==0) = [];
    toc;
    
    out.trainId(out.sum==0) = [];

    out.num_images          = numel(out.trainId);
    out.num_images_empty    = sum(out.sum==0);

    out.sum(out.sum==0)     = [];
    
    fprintf('Good images: %d\n', out.num_images);
    fprintf('Empty images: %d\n', out.num_images_empty);
end


