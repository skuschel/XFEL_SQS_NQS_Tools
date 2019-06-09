% gives the ring spacing distribution of the specified run list
clc;
clear;

run_nr_list=[342,343];
background_run_nr=341;

%read background
info.path=get_path(201802, 002195, 'raw', background_run_nr);
pnccd_background=pnccd_read(info);
background_mean=mean(pnccd_background.data,3);

mask=ones(1024,1024);

mask(491:511,483:543)=0;

full_opening_angle=120; %degrees
x=(1:1024);
y=(1:1024);
[X,Y]=meshgrid(x-512,y-512);
phi=atan2(X,Y);
mask(abs(phi)<pi-full_opening_angle/2*pi/180)=0;
% mask(512:end,:)=0;

nrad=400;
center.x=514;
center.y=534;


clear ring_spacings

figure(1339)


k=0;
for run_nr=run_nr_list
    hit_list_folder=[sprintf('/gpfs/exfel/exp/SQS/201802/p002195/usr/Shared/hit_lists') sprintf('/hits_run_%d.dat',run_nr)];
    hit_list=load(hit_list_folder);
    
    for u=1:numel(hit_list)
        k=k+1;
        
        path=get_path(201802, 002195, 'raw', run_nr);
        pnccd=pnccd_read(path,'trainId',hit_list(u));
        
        img_to_analyze=cast(pnccd.data,'double')-background_mean;
        [radiusAxis,radiusInt] = get_radial_integral(img_to_analyze,mask,0,center,nrad);
        
        minrad=max(find(radiusInt(isnan(radiusInt))));
        radiusInt(isnan(radiusInt))=0;
        radiusInt_filtered=lowpass(radiusInt.',1/8).';
        radiusInt_filtered(1:minrad)=NaN;
        
        subplot(1,2,1)
        hold off
        imagesc(x,y,(img_to_analyze.*mask))
        axis equal tight
        caxis([clim_lo clim_hi]);
        set(gca,'Colorscale','log')
        title(sprintf('%d: run nr: %d; trainId: %d',u,run_nr,pnccd.trainId))
        hold on
        plot_rings(center,100);
        size_img=300;
        xlim(512+[-size_img size_img])
        ylim(512+[-size_img size_img-200])
        
        subplot(2,2,2)
        [theta,rho]=cart2pol(x-center.x,y-center.y);
        surf(theta,rho,(img_to_analyze.*mask),'edgecolor','none');
        view(2)
        ylim([0 300])
        caxis([clim_lo clim_hi]);
        
        subplot(2,2,4);
        hold off
        plot(radiusAxis,radiusInt)
        hold on
        plot(radiusAxis,radiusInt_filtered,'linewidth',2)
        ring_positions=get_ring_pos(radiusInt_filtered);
        plot(radiusAxis(ring_positions),radiusInt_filtered(ring_positions),'rx','markersize',10)
        ring_spacings(k)=get_max_spacing(radiusAxis(ring_positions));
        set(gca,'yscale','log')
        xlim([0 500])
        title(sprintf('%.2f',ring_spacings(k)))
        drawnow
    end
end
%%
ax_hist_rs=linspace(0,200,50);
hist_spacing=hist(ring_spacings,ax_hist_rs);

figure()
bar(ax_hist_rs,hist_spacing)
xlabel('ring spacing')
title(sprintf('%d ',run_nr_list))
%%
function ring_positions=get_ring_pos(radius_int)
ind_ax=1:numel(radius_int);
grad_rI=gradient(radius_int,ind_ax);
grad_grad_rI=gradient(grad_rI,ind_ax);
[a,ring_positions]=find(grad_rI(1:numel(radius_int)-1).*grad_rI(2:numel(radius_int))<0);
ring_positions(grad_grad_rI(ring_positions)>0)=[];
end

function max_spacing=get_max_spacing(ring_r)
inx_ax=1:numel(ring_r)-1;
spacings=ring_r(inx_ax+1)-ring_r(inx_ax);

max_spacing=max(spacings);
end