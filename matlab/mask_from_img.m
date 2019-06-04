function [mask] = mask_from_img(mask_image_file)
mask=imread(mask_image_file);

mask(mask>0)=1;
mask=double(flipud(mask));

end