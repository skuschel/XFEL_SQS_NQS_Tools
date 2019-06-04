function out = get_files(path, expression)
    files = dir(path);
    files = files(3:end);

    out = files(~cellfun('isempty', regexp({files.name}, expression))); % get all files that contain the expression;
end