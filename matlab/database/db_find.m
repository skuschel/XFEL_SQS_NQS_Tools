function entries = db_find(db, fieldname, value)
    entries = [];
    
    for i=1:numel(db.entry)
        if ischar(value)
            if any(strcmp(db.entry(i).(fieldname), value))
               %entries = [entries, db.entry(i)];
               entries = [entries, i];
            end
        else if db.entry(i).(fieldname)==value
           %entries = [entries, db.entry(i)];
           entries = [entries, i];
        end
        
    end
end