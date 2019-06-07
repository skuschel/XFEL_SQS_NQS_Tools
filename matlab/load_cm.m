function [out] = load_cm()
    load('cm');
    
    % if function is called without output arguments save struct with name
    % 'au' else assign it to given output name
    if nargout==0
        assignin('caller', 'cm', cm);
    else
        out = cm;
    end
end