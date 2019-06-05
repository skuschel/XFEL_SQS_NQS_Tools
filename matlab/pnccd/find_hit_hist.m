function [is_hit,weakest_hit,strongest_non_hit] = find_hit_hist(pnccd_images_backsub,fac_hit,num_bins,plot_mode)
%takes a histogram of the sums of the background substracted images. Then
%classifies everything as a hit which is larger than fac_hit*median.
sums=squeeze(sum(sum(pnccd_images_backsub,1),2));
sum_x_vec=linspace(min(sums),max(sums),num_bins);
hist_sums=hist(sums,sum_x_vec);
hist_sums(1)=0;
median_hist=sum(hist_sums.*sum_x_vec)/sum(hist_sums);     

is_hit=find(sums>median_hist*fac_hit);
weakest_hit=find(min(sums(sums>median_hist*fac_hit))==sums);
strongest_non_hit=find(max(sums(sums<median_hist*fac_hit)));

if(plot_mode)
    subplot(2,2,2)
    hold off
    bar(sum_x_vec,(hist_sums));
    hold on
    plot([1 1]*median_hist,[0 max(hist_sums)],'r','linewidth',2)
    plot([1 1]*median_hist*fac_hit,[0 max(hist_sums)],'--r','linewidth',2)
end
end

