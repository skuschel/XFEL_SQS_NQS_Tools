% This script will export scattering patterns as .png images. It will use
% the hit database and the background database, so they have to be updated.
clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));

%__________________________________________________________________________

clim_lo=1e2;
clim_hi=0.5e4;
gap_size=4;

runs_to_export=[415,416,417];
all_runs_flag=0;
%__________________________________________________________________________

database_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');
image_save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_hits/');

db_runs=load([database_path 'db_runs.mat']);
db_hits=load([database_path 'db_hits.mat']);
db_bg=load([database_path 'db_bg_runs.mat']);

runs_all=db_get(db_hits,'run');
runs_bg_all=db_get(db_runs,'run_bg');
train_Ids_all=db_get(db_hits,'trainId');

if all_runs_flag
    runs_to_export=unique(runs_all);    %all images
end

ind_export_hits=db_find(db_hits,'run',runs_to_export);
ind_export_runs=db_find(db_runs,'run',runs_to_export);

run_nrs=runs_all(ind_export_hits);
train_Ids=train_Ids_all(ind_export_hits);

%%
mkdir(image_save_path);
fig=figure('position',[80 272 800 800]);
set(gcf,'Color','w')

for u=1:numel(train_Ids)
    fprintf('%d / %d \n',u,numel(train_Ids));
    
    curr_bg_run=db_get(db_runs,'run_bg',db_find(db_runs,'run',run_nrs(u)));
    
    if(curr_bg_run>0)
        info.path=get_path(201802, 002195, 'raw',  run_nrs(u));
        pnccd=pnccd_read(info,'trainId',train_Ids(u));
        bg_index=find(db_bg.run==curr_bg_run);
        bg_now=db_bg.mean(:,:,bg_index);
        image_now=pnccd.data-bg_now;
        
        imagesc(add_gap(image_now,gap_size))
        axis equal tight
        caxis([clim_lo clim_hi]);
        set(gca,'Colorscale','log')
        title(sprintf('run nr: %d; trainId: %d',run_nrs(u),train_Ids(u)))
        colorbar
        set(gca,'xticklabel',[])
        set(gca,'yticklabel',[])
        drawnow
        
        tic
        im_name=[image_save_path sprintf('run_%03d_trainId_%09d.png',run_nrs(u),train_Ids(u))];
        %         saveas(fig,im_name);
        F=getframe(fig);
        img=frame2im(F);
        imwrite(img,im_name);
        toc
    end
end