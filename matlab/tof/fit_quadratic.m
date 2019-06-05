% function [fit, x] = fit_quadratic(xdata, ydata)
%     lb = [0, 0];
%     ic = [1, 1e5];
%     ub = [1e3, 1e7];
% 
%     opts = optimset('MaxFunEvals', 10000, 'MaxIter', 10000, 'Display', 'off', 'FunValCheck', 'on', 'TolFun', 1e-15, 'TolX', 1e-15);
%     
%     x = lsqcurvefit(@(x,xdata) x(1)*(xdata-x(2)).^2, ic, xdata, ydata, lb, ub, opts);
%     
%     
%     fit = x(1)*(xdata-x(2)).^2;
% end

% 
% function [fit, x, res] = fit_quadratic(xdata, ydata)
%     lb = [0, 0, -100, -10, 0];
%     ic = [1, 1e5, 0, 0, 1e5];
%     ub = [1e3, 1e7, 100, 10, 1e7];
% 
%     opts = optimset('MaxFunEvals', 10000, 'MaxIter', 10000, 'Display', 'on', 'FunValCheck', 'on', 'TolFun', 1e-25, 'TolX', 1e-25);
%     
%     [x, res] = lsqcurvefit(@(x,xdata) x(3) + x(1)*(xdata-x(2)).^2 + x(4)*(xdata-x(5)), ic, xdata, ydata, lb, ub, opts);
%     
%     
%     fit = x(3) + x(1)*(xdata-x(2)).^2 + x(4)*(xdata-x(5));
% end





function [fit, x, res] = fit_quadratic(xdata, ydata)
    lb = [0, 0, -100];
    ic = [1, 1e5, 0];
    ub = [1e3, 1e7, 100];

    opts = optimset('MaxFunEvals', 10000, 'MaxIter', 10000, 'Display', 'on', 'FunValCheck', 'on', 'TolFun', 1e-50, 'TolX', 1e-50);
    
    [x, res] = lsqcurvefit(@(x,xdata) x(3) + x(1)*(xdata-x(2)).^2, ic, xdata, ydata, lb, ub, opts);
    
    fit = x(3) + x(1)*(xdata-x(2)).^2;
end