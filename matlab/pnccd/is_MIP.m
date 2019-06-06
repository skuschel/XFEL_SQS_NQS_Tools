function [mip] = is_MIP(image,nbins,mip_th)
    h_x=linspace(cast(min(min(image)),'double'),cast(max(max(image)),'double'),nbins);
    histo=hist(image(:),h_x);
    histo(1)=0;
    
    median=sum(histo.*h_x)/sum(histo);
    mip=max(h_x>median*mip_th);
end

