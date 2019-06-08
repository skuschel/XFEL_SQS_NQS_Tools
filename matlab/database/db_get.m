function out = db_get(db, fieldname)
    out = [];
    
    for i=1:numel(db.entry)
        if isfield(db.entry(i), fieldname)
           out = [out; db.entry(i).(fieldname)];
        end
    end
end