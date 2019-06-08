function out = pnccd_read(info, varargin)
    if nargin==1
        out = pnccd_read_all(info);
    else if nargin==3
        switch varargin{1}
            case 'files'
                out = pnccd_read_all(info, varargin{2}); 
            case 'trainId'
                out = pnccd_read_single(info, varargin{2});    
            otherwise
            out = [];
        end
        end
        
        tic;
        out.data = rot90(out.data);
        toc;
end


