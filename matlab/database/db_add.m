function db = db_add(db, entry, varargin)
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
    
    if nargin==2
        db.entry(entries+1) = entry;
    else
        fieldname = varargin{1};
        
        idx = db_find(db, fieldname, entry.(fieldname));
       
        if isempty(idx)
            db.entry(entries+1) = entry;    % no conflicts found, just insert the entry at the end of the database
        else
            if nargin==3
%                 disp('Conflict found, keeping!')
                % if a conflict is found and the 'overwrite' option is not set, keep the existing database entry
            else
                switch varargin{2}
                    case 'overwrite'
%                         disp('Conflict found, overwriting!');
                        db.entry(idx) = entry;
                    otherwise
%                     disp('Conflict found, otherwise!')
                end
            end
        end
    end
end

