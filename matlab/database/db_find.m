function entries = db_find(db, fieldname, value)
    entries = [];
    
    for i=1:numel(db.entry)
        if ischar(value)
            if any(strcmp(db.entry(i).(fieldname), value))
               entries = [entries, i];
            end
        else
            if ~isempty(intersect(db.entry(i).(fieldname), value))
%            elseif db.entry(i).(fieldname)==value      
           entries = [entries, i];
        end
    end
end
