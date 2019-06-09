function out = db_get(db, fieldname, varargin)
    out = [];
    
    if nargin==2
        for i=1:numel(db.entry)
            if isfield(db.entry(i), fieldname)
               out = [out; db.entry(i).(fieldname)];
            end
        end
    else
        for i=varargin{1}
            if isfield(db.entry(i), fieldname)
               out = [out; db.entry(i).(fieldname)];
            end
        end
    end
end