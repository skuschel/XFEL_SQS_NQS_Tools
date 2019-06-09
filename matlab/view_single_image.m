clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));

%__________________________________________________________________________

clim_lo=1e2;
clim_hi=0.5e4;
gap_size=4;

center.x=514;
center.y=534;
   
trainId_to_plot=136324473;

%__________________________________________________________________________
%load databases

database_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');

db_runs=load([database_path 'db_runs.mat']);
db_hits=load([database_path 'db_hits.mat']);
db_bg=load([database_path 'db_bg_runs.mat']);

run_now=db_get(db_hits,'run',db_find(db_hits,'trainId',trainId_to_plot));

curr_bg_run=db_get(db_runs,'run_bg',db_find(db_runs,'run',run_now));

bg_index=find(db_bg.run==curr_bg_run);
bg_now=db_bg.mean(:,:,bg_index);

%load image
info.path=get_path(201802, 002195, 'raw', run_now);
pnccd=pnccd_read(info,'trainId',trainId_to_plot);
image_now=pnccd.data-bg_now;

%% plot the figure
figure(123)
subplot(1,2,1)
hold off
imagesc(add_gap(image_now,gap_size))
axis equal tight
caxis([clim_lo clim_hi]);
set(gca,'Colorscale','log')
title(sprintf('run nr: %d; trainId: %d',run_now,pnccd.trainId))
colorbar
% plot_rings(center,100);

mask=ones(1024,1024);

mask(483:543,491:511)=0;
full_opening_angle=120; %degrees
x=(1:1024);
y=(1:1024);
[X,Y]=meshgrid(x-512,y-512);
phi=atan2(Y,X);
mask(abs(phi)<pi-full_opening_angle/2*pi/180)=0;
nrad=400;

[radiusAxis,radiusInt] = get_radial_integral(image_now,mask,0,center,nrad);

subplot(1,2,2)
hold off
plot(radiusAxis,radiusInt)
set(gca,'yscale','log')
xlim([0 500])
xlabel('radius in px')