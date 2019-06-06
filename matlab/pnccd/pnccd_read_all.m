function out = pnccd_read_all(info, varargin)
    out = pnccd_read_trainId(info);

    out.num_images = sum(out.trainId>0);

    out.data = zeros(1024,1024,out.num_images, 'uint16');

    files = get_files(info.path, 'PNCCD01');

    out.trainId = [];

    for i=1:numel(files)
        if nargin>1
            files_in = varargin{1};
            if sum(files_in==i)==0
               continue; 
            end
        end
        
        fprintf('Loading pnccd file %02d/%02d\n', i, numel(files));
        path_full = sprintf('%s/%s', files(i).folder, files(i).name);

        pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';
        pnccd_image     = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image';
        
        current_trainIds = h5read(path_full, pnccd_trainId);
        
        idx = 1:numel(current_trainIds);
        
        roi = current_trainIds>0;
        idx = idx(roi);
        
        idx_end = 0;
        if (~isempty(idx))
            out.trainId = [out.trainId; current_trainIds(roi)];
        
            idx_start = idx_end+1;
            idx_end = idx_start+numel(idx)-1;

            out.data(:, :, idx_start:idx_end) = h5read(path_full, pnccd_image, [1,1,1], [1024,1024,numel(idx)]);
        end
    end

    out.num_images          = numel(out.trainId);
end








% old version (this is testde and workds well)

% function out = pnccd_read_all(info, varargin)
%     files = get_files(info.path, 'PNCCD01');
% 
%     out.data = [];
%     out.trainId = [];
% 
%     tic;
%     for i=1:numel(files)
%         if nargin>1
%             files_in = varargin{1};
%             if sum(files_in==i)==0
%                continue; 
%             end
%         end
%         
%         fprintf('Loading pnccd file %02d/%02d\n', i, numel(files));
%         path_full = sprintf('%s/%s', files(i).folder, files(i).name);
% 
%         pnccd_trainId   = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/trainId';
%         pnccd_image     = '/INSTRUMENT/SQS_NQS_PNCCD1MP/CAL/PNCCD_FMT-0:output/data/image';
%         
%         out.trainId = [out.trainId; h5read(path_full, pnccd_trainId)];
%         out.data   = cat(3, out.data, h5read(path_full, pnccd_image));
%     end
%     toc;
% 
%     fprintf('Casting images to double...\n');
%     tic;
%     out.data = cast(out.data, 'double');
%     toc;
%     
%     out.sum  = squeeze(sum(sum(out.data, 1), 2));
% 
% 
%     fprintf('Removing empty images...\n');
%     tic;
%     out.data(:,:, out.sum==0) = [];
%     toc;
%     
%     out.trainId(out.sum==0) = [];
% 
%     out.num_images          = numel(out.trainId);
%     out.num_images_empty    = sum(out.sum==0);
% 
%     out.sum(out.sum==0)     = [];
%     
%     fprintf('Good images: %d\n', out.num_images);
%     fprintf('Empty images: %d\n', out.num_images_empty);
% end


