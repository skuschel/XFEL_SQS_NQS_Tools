function out = pnccd_read(path, varargin)
    tic;
    if nargin==1
        out = pnccd_read_all(path);
    elseif nargin==3
        switch varargin{1}
            case 'files'
                out = pnccd_read_all(path, varargin{2}); 
            case 'trainId'
                out = pnccd_read_single(path, varargin{2});    
            otherwise
            out = [];
        end
    end
    toc;
    
    disp('Transposing all images');
    tic;
    out.data = rot90(out.data);
    out.data = flip( out.data, 1);
    toc;
end



