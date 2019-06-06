clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));
addpath('/home/bkruse/analysis_scripts')
%________________________________________________
%for plotting the image
gap_size=3; %mm

clim_lo=1e2;
clim_hi=1e4;

%run numbers
run_nr=203;
background_run_nr=203;

%settings for hit finding
fac_hit=2.5;
num_bins=200;

%_________________________________________________

info.path=get_path(201802, 002195, 'raw', run_nr);
pnccd=read_pnccd(info);

%specify background images here!
% info.path=get_path(201802, 002195, 'raw', background_run_nr);
% pnccd_background=read_pnccd(info);
% background_images=pnccd_background;
background_images=0;%pnccd.data(:,:,1:100);

fprintf('analyzing %d images... \n',pnccd.num_images);
%% substract the background
background_mean=mean(pnccd.data,3);
background=max(background_images,[],3);
pnccd_images_backsub=pnccd.data-repmat(background,1,1,pnccd.num_images);
pnccd_images_backsub(pnccd_images_backsub<0)=0;     %set everything below zero to zero
%%
figure(1)

[is_hit,weakest_hit,strongest_non_hit] = find_hit_hist(pnccd_images_backsub,fac_hit,num_bins,1);
if(isempty(is_hit))
    fprintf('No Hits! Terminated excecution.\n');
    return;
end

%plot weakest hit and strongest non-hit
subplot(2,2,1)
imagesc(add_gap(pnccd_images_backsub(:,:,weakest_hit),gap_size).')
axis equal tight
caxis([clim_lo clim_hi]);
set(gca,'Colorscale','log')
title(sprintf('weakest hit; run nr: %d; trainId: %d',run_nr,pnccd.trainId(weakest_hit)))

subplot(2,2,3)
imagesc(add_gap(pnccd_images_backsub(:,:,strongest_non_hit),gap_size).')
axis equal tight
caxis([clim_lo clim_hi]);
set(gca,'Colorscale','log')
title('strongest non-hit')

fprintf('number of hits: %d / %d; hit-rate: %.2f percent \n',numel(is_hit),pnccd.num_images,100*numel(is_hit)/pnccd.num_images)
%%
%plot all hits to browse through
figure(2)
for u=1:pnccd.num_images
% for u=is_hit.'
% for u=2951

    %plot the image with mean background substracted
    subplot(1,2,1)
    hold off
    imagesc(add_gap(pnccd.data(:,:,u)-background_mean,gap_size).')
    axis equal tight
    caxis([clim_lo clim_hi]);
    set(gca,'Colorscale','log')
    title(sprintf('%d: run nr: %d; trainId: %d',u,run_nr,pnccd.trainId(u)))
    
    %plot the image with max background substracted (used for hit finding)
    subplot(1,2,2)
    hold off
    imagesc(add_gap(pnccd_images_backsub(:,:,u),gap_size).')
    axis equal tight
    caxis([clim_lo clim_hi]);
    set(gca,'Colorscale','log')
    title(sprintf('run nr: %d; trainId: %d',run_nr,pnccd.trainId(u)))
    
    drawnow
%     pause(1)
end
subplot(1,2,1)
colorbar
subplot(1,2,2)
colorbar

%%
% save_ind=2293;
% img_2_save=add_gap(pnccd.data(:,:,save_ind),gap_width).';
% save_path='/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_for_recreation/';
% save([save_path sprintf('run_%d_bunchid_%d.dat',run_nr,pnccd_trainIDs(save_ind))],'img_2_save','-ascii')