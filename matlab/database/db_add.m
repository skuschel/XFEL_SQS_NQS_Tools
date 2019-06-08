function db = db_add(db, entry)
    if isempty(db)
        entries = 0;
    else
        if ~isfield(db, 'entry')
            entries = 0;
        else
            entries = numel(db.entry);
        end
    end
    
    db.latest_update = datestr(datetime('now'), 'dd.mm.yyyy HH:MM:SS');
    
    db.entry(entries+1) = entry;
end

