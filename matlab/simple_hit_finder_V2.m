clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));
database_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');


db_runs=load([database_path 'db_runs.mat']);
db_bg=load([database_path 'db_bg_runs.mat']);
db_hits=load([database_path 'db_hits.mat']);
%__________________________________________________________________________
%for plotting the image
gap_size=4.3; %mm

clim_lo=1e2;
clim_hi=0.5e4;

%run numbers
run_nr=         429;
run_bg_nr=      426;
run_dark_nr=    425;

save_data_flag=0;   %save trainIds of hits and the images as .dat ?
plot_flag=1;

%settings for hit finding
% fac_hit=2.7;    %for runs before run 187
% fac_hit=1.7;
fac_hit=1.5;
num_bins=100000;      %number of bins for hit finding histogram
mip_th=100;          %MIP finder threshold
nbins_MIP=2000;
%__________________________________________________________________________
path=get_path(201802, 002195, 'raw', run_nr);
pnccd=pnccd_read(path);
% pnccd=pnccd_read(path,'files',1:6);
% tof=read_tof(path);

%background
% run_bg_nr=db_get(db_runs,'run_bg',db_find(db_runs,'run',run_nr)); %get corresponding background run
bg_index=find(db_bg.run==run_bg_nr);

fprintf('analyzing %d images... \n',pnccd.num_images);

num_bins=num_bins*pnccd.num_images/12e3;
%% subtract the background
background_mean=db_bg.mean(:,:,bg_index);
background_max=db_bg.max(:,:,bg_index);
pnccd_images_backsub=pnccd.data-repmat(background_max,1,1,pnccd.num_images);
%% finding hits
figure(1)
[is_hit,weakest_hit,strongest_non_hit] = find_hit_hist(pnccd_images_backsub,fac_hit,num_bins,1);

% finding MIPs
MIPs_found=0;
for u=is_hit.'
    if(is_MIP(pnccd_images_backsub(:,:,u),nbins_MIP,mip_th))
        title(sprintf('%d: run nr: %d; trainId: %d',u,run_nr,pnccd.trainId(u)))
        is_hit(is_hit==u)=[];
        MIPs_found=MIPs_found+1;
    end
end
fprintf('Sorted out %d MIPs.\n',MIPs_found);

if(isempty(is_hit))
    fprintf('No Hits! Terminated excecution.\n');
    return;
end

%plot weakest hit and strongest non-hit
subplot(2,2,1)
% imagesc(add_gap(pnccd_images_backsub(:,:,weakest_hit),gap_size).')
imagesc(add_gap(cast(pnccd.data(:,:,weakest_hit),'double')-background_mean,gap_size))
axis equal tight
caxis([clim_lo clim_hi]);
set(gca,'Colorscale','log')
title(sprintf('weakest hit; run nr: %d; trainId: %d',run_nr,pnccd.trainId(weakest_hit)))

subplot(2,2,3)
% imagesc(add_gap(pnccd_images_backsub(:,:,strongest_non_hit),gap_size).')
imagesc(add_gap(cast(pnccd.data(:,:,strongest_non_hit),'double')-background_mean,gap_size))
axis equal tight
caxis([clim_lo clim_hi]);
set(gca,'Colorscale','log')
title('strongest non-hit')

fprintf('number of hits: %d / %d; hit-rate: %.2f percent \n',numel(is_hit),pnccd.num_images,100*numel(is_hit)/pnccd.num_images)
%% plot all hits to browse through
if(plot_flag)
    figure(12)
    % for u=1:pnccd.num_images
    %     if(sum(u==is_hit)==0)
    for u=is_hit.'
        %     if(is_MIP(pnccd_images_backsub(:,:,u),nbins_MIP,mip_th))
        % for u=655
        
        %plot the image with mean background substracted
        subplot(1,2,1)
        hold off
        imagesc(add_gap(cast(pnccd.data(:,:,u),'double')-background_mean,gap_size))
        axis equal tight
        caxis([clim_lo clim_hi]);
        set(gca,'Colorscale','log')
        title(sprintf('%d: run nr: %d; trainId: %d',u,run_nr,pnccd.trainId(u)))
        
        %plot the image with max background substracted (used for hit finding)
        subplot(2,2,2)
        hold off
        imagesc(add_gap(pnccd_images_backsub(:,:,u),gap_size))
        axis equal tight
        caxis([clim_lo clim_hi]);
        set(gca,'Colorscale','log')
        title(sprintf('run nr: %d; trainId: %d',run_nr,pnccd.trainId(u)))
        
        %     subplot(2,2,4)
        %     plot(tof.data(:,u))
        %     ylim([-2000 1780])
        
        %     colormap(jet(256))
        drawnow
        %     pause(0.5)
        %     end
    end
    subplot(1,2,1)
    
    colorbar
    subplot(2,2,2)
    colorbar
end
%% SAVING??
if(save_data_flag)
    
    %save to database
    for i=1:numel(is_hit)
        entry_hits.trainId=pnccd.trainId(is_hit(i));
        entry_hits.run=run_nr;
        db_hits=db_add(db_hits,entry_hits,'trainId','overwrite');
    end
    entry_run.run=run_nr;
    entry_run.run_bg=run_bg_nr;
    entry_run.run_dark=run_dark_nr;
    entry_run.meta.hitrate=100*numel(is_hit)/pnccd.num_images;
    db_runs=db_add(db_runs,entry_run,'run','overwrite');
    
    save([database_path 'db_hits.mat'],'-struct','db_hits');
    save([database_path 'db_runs.mat'],'-struct','db_runs');
    
    %save hit list
    fprintf('saving trainIds \n')
    save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/hit_lists/');
    mkdir(save_path)
    trainid_list=cast(pnccd.trainId(is_hit),'double');
    fid=fopen([save_path sprintf('hits_run_%d.dat',run_nr)],'wt');
    fprintf(fid,'%d \n',trainid_list);
    fclose(fid);
    
    %save mat files
    fprintf('saving hits as mat files...\n')
    save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_for_recreation/Run_%d/',run_nr);
    mkdir(save_path);
    for save_ind=is_hit.'
        img_2_save=cast(pnccd.data(:,:,save_ind),'double');
        %   save([save_path sprintf('run_%d_bunchid_%d.dat',run_nr,pnccd.trainId(save_ind))],'img_2_save','-ascii')
        save([save_path sprintf('run_%d_bunchid_%d.mat',run_nr,pnccd.trainId(save_ind))],'img_2_save')
    end
end
fprintf('done!\n');