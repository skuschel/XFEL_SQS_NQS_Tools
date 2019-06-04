function [radiusAxis,radiusInt] = get_radial_integral(imgInt,imgMask,minval,center,nrad)

imgInt(imgInt<minval)=0;    %remove pixels that are too low

xaxis=1:size(imgInt,1);
yaxis=1:size(imgInt,2);
[X,Y]=meshgrid(yaxis,xaxis);
imgRadius=sqrt((X-center.x).^2+(Y-center.y).^2);
radiusAxis=linspace(0,max(max(imgRadius)),nrad);

dr=radiusAxis(2)-radiusAxis(1);
radiusInt=radiusAxis*0;
radiusInt_entries=radiusAxis*0;

id_bin=(floor(imgRadius/dr)+1).*imgMask;

for loop=1:numel(imgRadius)
   bin_act=id_bin(loop);
   if(bin_act>0)
      radiusInt(bin_act)=radiusInt(bin_act)+imgInt(loop);
      radiusInt_entries(bin_act)=radiusInt_entries(bin_act)+1;
   end
end

radiusInt=radiusInt./radiusInt_entries;

end