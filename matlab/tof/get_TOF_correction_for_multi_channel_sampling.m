function [data] = get_TOF_correction_for_multi_channel_sampling(data,bg,samples)
    for idx=1:samples
        data_idx_selection=idx:samples:numel(data);
        data_exerpt=data(data_idx_selection);
        if(~isnan(bg))
           data_exerpt=data_exerpt - mean(data_exerpt(bg(1):bg(2)));
        end
        data(data_idx_selection)=data_exerpt;
    end
end