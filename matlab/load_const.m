function out = load_const()

    const.u = 1.66053892173e-27; % atomic mass in [kg]


    if nargout==0
        assignin('caller', 'const', const);
    else
        out = const;
    end
end