function [fit, x, res] = fit_quadratic(xdata, ydata)
    lb = [0, 0, -100];
    ic = [1, 1e5, 0];
    ub = [1e3, 1e7, 100];

    opts = optimset('MaxFunEvals', 10000, 'MaxIter', 10000, 'Display', 'off', 'FunValCheck', 'on', 'TolFun', 1e-50, 'TolX', 1e-50);
    
    [x, res] = lsqcurvefit(@(x,xdata) x(3) + x(1)*(xdata-x(2)).^2, ic, xdata, ydata, lb, ub, opts);
    
    fit = x(3) + x(1)*(xdata-x(2)).^2;
end