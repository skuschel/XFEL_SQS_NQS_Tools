clc;
clear;

dark_nr=107;
run_nr=161;

addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));
% addpath '/home/bkruse/analysis_scripts/development_area';

% dark.path=get_path(201802, 002195, 'raw', dark_nr);
% pnccd_dark=read_pnccd(dark);

info.path=get_path(201802, 002195, 'raw', run_nr);
pnccd=read_pnccd(info);

% pnccd_dark=cast(pnccd_dark.data,'double');
pnccd_images=cast(pnccd.data,'double');
pnccd_trainIDs=pnccd.trainId;

num_images=numel(pnccd_images(1,1,:));
%%
sums=sum(sum(pnccd_images,1),2);
% figure
% plot(squeeze(sums),'.')
%%
% pnccd_dark_now=pnccd_dark(:,:,1);
lit_pix_th=5e3;
lit_pix_num_th=4e5;

pnccd_images=pnccd_images(:,:,sums>0);

background=mean(pnccd_images,3);

lit_pix_vec=[];
hit_rate_vec=[];

disp(numel(pnccd_images(1,1,:)))
figure(2)
for u=1:numel(pnccd_images(1,1,:))
% for u=58
    subplot(1,2,1)
    img_now=pnccd_images(:,:,u)-background;
    imagesc(add_gap(img_now,round(3/0.075)).')
    axis equal tight
    caxis([-0.0e4 0.5e4]);
    title(sprintf('run nr: %d; bunchid: %d',run_nr,pnccd_trainIDs(u)))

    lit_pix_vec=[lit_pix_vec sum(img_now(img_now>lit_pix_th))];
    hit_rate_vec=[hit_rate_vec sum(img_now(img_now>lit_pix_th))>lit_pix_num_th];
    
    subplot(2,2,2)
    plot((lit_pix_vec))
    subplot(2,2,4)
    plot(cumsum(hit_rate_vec))
    

    drawnow
end