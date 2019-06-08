% This script will export scattering patterns as .png images. It will use
% the hit database and the background database, so they have to be updated.

clc;
clear;
%___________

clim_lo=1e2;
clim_hi=0.5e4;
gap_size=4;

runs_to_export=[353;354];
%____________
database_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');
bg_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');
image_save_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/images_hits/');

db=load([database_path 'db_hits.mat']);
db_bg=load([bg_path 'db_bg_runs.mat']);

for u=1:numel(db.entry)
    bg_run_nrs_in(u)=db.entry(u).run_bg;
    run_nrs_in(u)=db.entry(u).run;
    train_Ids_in(u)=db.entry(u).trainId;
end

bg_run_nrs=[];
run_nrs=[];
train_Ids=[];
for u=1:numel(runs_to_export)
    ind_export=find(run_nrs_in==runs_to_export(u));
    bg_run_nrs=[bg_run_nrs bg_run_nrs_in(ind_export)];
    run_nrs=[run_nrs run_nrs_in(ind_export)];
    train_Ids=[train_Ids train_Ids_in(ind_export)];
end
%%
mkdir(image_save_path);
fig=figure('position',[80 272 600 600]);

for u=1:numel(train_Ids)
    if(bg_run_nrs(u)>0)
        info.path=get_path(201802, 002195, 'raw',  run_nrs(u));
        pnccd=pnccd_read(info,'trainId',train_Ids(u));
        bg_index=find(db_bg.run==bg_run_nrs(u));
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
        saveas(fig,[image_save_path sprintf('run_%03d_trainId_%09d.png',run_nrs(u),train_Ids(u))]);
        toc
    end
end