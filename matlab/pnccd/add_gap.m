function [image] = add_gap(image, gap_width)
    py = 0.075; % pixel size in mm

    gap_pixels = round(gap_width / py);
    
    xaxis = 1:size(image,1);
    yaxis = 1:size(image,2);

    image = [image(1:(max(yaxis)/2), xaxis); zeros(gap_pixels, numel(xaxis)); image((max(yaxis)/2+1):max(yaxis), xaxis)];
end

