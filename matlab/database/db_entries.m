function entries = db_entries(db, index_list)
    entries = [];
    
    for index = index_list
        entries = [entries, db.entry(index)];
    end
end