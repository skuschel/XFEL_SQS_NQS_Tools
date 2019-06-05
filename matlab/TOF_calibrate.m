clear;
clc;

load_const;

addpath(genpath('../matlab'));


info.path = get_path(201802, 002195, 'raw', 108);

tof = read_tof(info);


tof_size = size(tof.data, 1);
tof_avg = mean(tof.data, 2);
tof_avg = get_TOF_correction_for_multi_channel_sampling(tof_avg, [1, 3e4], 16);


t_index = 1:tof_size;



m_Xe131 = 1; % 130.90508259*const.u;
t_idx_list = [78426, 69842, 66090];
ooq_list   = m_Xe131./[2, 6, 13];

[fit, par] = fit_quadratic(t_idx_list, ooq_list);


figure
moq_calibrated = par(1)*(t_index-par(2)).^2;
plot(t_index, moq_calibrated);
hold on;
plot(t_idx_list, ooq_list, 'o');
xlabel('Uncalibrated flight time [bins]');
ylabel('Xenon mass / charge state');


roi = t_index>=par(2);

figure;
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([0, 50])
xlabel('Charge state / mass of Xe^{131}');
ylabel('Ion yield [arb. units]');

grid on;



