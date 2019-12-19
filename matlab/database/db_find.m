function entries = db_find(db, fieldname, value)
    entries = [];
    
    if ~isfield(db, 'entry')
       return; 
    end
    
    for i=1:numel(db.entry)
        if ischar(value)
            if any(strcmp(db.entry(i).(fieldname), value))
               entries = [entries, i];
            end
        else  
            if sum(value==(db.entry(i).(fieldname))) > 0
                entries = [entries, i];
            end
        end
    end
end







% old (much slower) version

% function entries = db_find(db, fieldname, value)
%     entries = [];
%     
%     if ~isfield(db, 'entry')
%        return; 
%     end
%     
%     for i=1:numel(db.entry)
%         if ischar(value)
%             if any(strcmp(db.entry(i).(fieldname), value))
%                entries = [entries, i];
%             end
%         else if ~isempty(intersect(db.entry(i).(fieldname), value))   
%            entries = [entries, i];
%         end
%     end
% end