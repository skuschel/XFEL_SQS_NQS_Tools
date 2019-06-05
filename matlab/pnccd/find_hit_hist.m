function [is_hit] = find_hit_hist(pnccd_images_backsub,fac_hit,num_bins)
%takes a histogram of the sums of the background substracted images. Then
%classifies everything as a hit which is larger than fac_hit*median.
sums=squeeze(sum(sum(pnccd_images_backsub,1),2));
sum_x_vec=linspace(min(sums),max(sums)/10,num_bins);
hist_sums=hist(sums,sum_x_vec);
hist_sums(1)=0;
median_hist=sum(hist_sums.*sum_x_vec)/sum(hist_sums);     

is_hit=find(sums>median_hist*fac_hit);


% figure
% bar(sum_x_vec,(hist_sums));
% hold on
% plot([1 1]*median_hist,[0 max(hist_sums)],'r','linewidth',2)
% plot([1 1]*median_hist*fac_hit,[0 max(hist_sums)],'--r','linewidth',2)
end

