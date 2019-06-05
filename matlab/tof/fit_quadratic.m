function [fit, x] = fit_quadratic(xdata, ydata)
    lb = [0, 0];
    ic = [1, 1e5];
    ub = [1e3, 1e7];

    opts = optimset('MaxFunEvals', 10000, 'MaxIter', 10000, 'Display', 'off', 'FunValCheck', 'on', 'TolFun', 1e-15, 'TolX', 1e-15);
    
    x = lsqcurvefit(@(x,xdata) x(1)*(xdata-x(2)).^2, ic, xdata, ydata, lb, ub, opts);
    
    
    fit = x(1)*(xdata-x(2)).^2;
end