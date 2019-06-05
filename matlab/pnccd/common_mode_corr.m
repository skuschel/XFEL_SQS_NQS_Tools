function [image] = common_mode_corr(image,nbins)
size_x=numel(image(:,1))/2;
size_y=numel(image(1,:))/2;

bright_ax=linspace(min(min(image)),max(max(image)),nbins);

% figure
for quadrant_1=0:1
    for quadrant_2=0:1
        for u=quadrant_1*size_x+(1:size_x)
            zeile=image(u,(size_y*(quadrant_2)+1):size_y*(quadrant_2+1));
            
            hist_zeile=hist(zeile,bright_ax);
            median_zeile=sum(hist_zeile.*bright_ax)/sum(hist_zeile);     
%             varianz_zeile=sum(hist_zeile.*(bright_ax-median_zeile).^2)/sum(hist_zeile);     

%             hold off
%             bar(bright_ax,hist_zeile)
%             hold on
%             plot([1 1]*median_zeile,[1 1]*100,'r');
%             drawnow
            
            image(u,(size_y*(quadrant_2)+1):size_y*(quadrant_2+1))=zeile-median_zeile;
        end
    end
end
end