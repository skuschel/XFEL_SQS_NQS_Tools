function [image] = add_gap(image,gap_width)
xaxis=1:size(image,1);
yaxis=1:size(image,2);

image=[image(xaxis,1:(max(yaxis)/2)) zeros(numel(xaxis),gap_width) image(xaxis,(max(yaxis)/2+1):max(yaxis))];
end

