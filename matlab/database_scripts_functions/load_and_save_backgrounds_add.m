% This script will add selected background runs to the background database.
clc;
clear;
addpath(genpath('/home/bkruse/git_code/XFEL_SQS_NQS_Tools/matlab/'));

%________________________________________________________________________
database_path=sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/');

runs_to_export=[476];
%________________________________________________________________________

db_bg=load([database_path 'db_bg_runs.mat']);

initial_size=numel(db_bg.run);

k=0;
for background_run_nr=runs_to_export.'
    if(sum(db_bg.run==background_run_nr)==0)
        k=k+1;
        
        path=get_path(201802, 002195, 'raw', background_run_nr);
        pnccd_background=pnccd_read(path);
        background_images=pnccd_background.data;
        
        background_mean=mean(background_images,3);
        background_max=max(background_images,[],3);
        
        db_bg.run(initial_size+k)=background_run_nr;
        db_bg.mean(:,:,initial_size+k)=background_mean;
        db_bg.max(:,:,initial_size+k)=background_max;
        
        fprintf('Added background run %d to background database. \n',background_run_nr);
    else
        fprintf('skipped run %d because it was already in the background database. \n',background_run_nr);
    end
end
save([database_path sprintf('db_bg_runs.mat')],'-struct','db_bg')