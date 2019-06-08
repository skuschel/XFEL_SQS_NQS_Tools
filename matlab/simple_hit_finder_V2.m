clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));

%________________________________________________
%for plotting the image
gap_size=3.3; %mm

clim_lo=1e2;
clim_hi=0.5e4;

%run numbers
run_nr=374;
background_run_nr=372;

save_data_flag=0;   %save trainIds of hits and the images as .dat ?

%settings for hit finding
% fac_hit=2.7;    %for runs before run 187
fac_hit=1.7;
num_bins=2000;      %number of bins for hit finding histogram
mip_th=30;          %MIP finder threshold
nbins_MIP=2000;
%_________________________________________________

info.path=get_path(201802, 002195, 'raw', run_nr);
pnccd=pnccd_read(info);
% pnccd=pnccd_read(info,'files',1:11);
% tof=read_tof(info);

%specify background images here!
info.path=get_path(201802, 002195, 'raw', background_run_nr);
pnccd_background=pnccd_read(info);
background_images=pnccd_background.data;
% background_images=pnccd.data(:,:,1:100);

fprintf('analyzing %d images... \n',pnccd.num_images);
%% substract the background
background_mean=mean(background_images,3);
background=max(background_images,[],3);
pnccd_images_backsub=pnccd.data-repmat(background,1,1,pnccd.num_images);
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
figure(2)
% for u=1:pnccd.num_images
for u=is_hit.'
% for u=2951
    
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
    pause(0.5)
end
subplot(1,2,1)
% size_img=400;
% xlim(512+[-size_img size_img])
% ylim(512+[-size_img size_img]+gap_size)
colorbar
subplot(2,2,2)
colorbar
%% SAVING??
if(save_data_flag)
    fprintf('saving trainIds \n')
    save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/hit_lists/');
    mkdir(save_path)
    trainid_list=cast(pnccd.trainId(is_hit),'double');
    fid=fopen([save_path sprintf('hits_run_%d.dat',run_nr)],'wt');
    fprintf(fid,'%d \n',trainid_list);
    fclose(fid);
    
    fprintf('saving images...\n')
    save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_for_recreation/Run_%d/',run_nr);
    mkdir(save_path);
    for save_ind=is_hit.'
        img_2_save=cast(pnccd.data(:,:,save_ind),'double');
%   save([save_path sprintf('run_%d_bunchid_%d.dat',run_nr,pnccd.trainId(save_ind))],'img_2_save','-ascii')
        save([save_path sprintf('run_%d_bunchid_%d.mat',run_nr,pnccd.trainId(save_ind))],'img_2_save')
    end
end
fprintf('done!\n');