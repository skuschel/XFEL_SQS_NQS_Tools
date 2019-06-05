%% ===== load and plot TOF raw data =====
clear;
clc;

load_const;

addpath(genpath('../matlab'));

info.path = get_path(201802, 002195, 'raw', 199);

tof = read_tof(info);

tof_size = size(tof.data, 1);
tof_avg = mean(tof.data, 2);
tof_avg = get_TOF_correction_for_multi_channel_sampling(tof_avg, [1, 3e4], 16);

t_index = 1:tof_size;

figure;
plot(t_index, tof_avg, 'r');
xlim([57591, 81017])



%% ===== quadratic curve fitting =====
m_Xe131 = 1; % 130.90508259*const.u;
% t_idx_list = [78426, 69842, 66090];
% t_idx_list = [76946, 68989, 65507, 64779];
% ooq_list   = m_Xe131./[2, 6, 13, 16];

% t_idx_list = [75195, 72901, 68578, 66323];
% ooq_list   = m_Xe131./[3, 4, 8, 13];

t_idx_list = [75194,  68579, 66325];            % used to calibrate run 199
ooq_list   = m_Xe131./[3, 8, 13];

[fit, par, res] = fit_quadratic(t_idx_list, ooq_list);

disp(res);

figure;
subplot(2,1,1);
moq_calibrated = par(1)*(t_index-par(2)).^2;
plot(t_index, moq_calibrated);
hold on;
plot(t_idx_list, ooq_list, 'o');
xlabel('Uncalibrated flight time [bins]');
ylabel('Xenon mass / charge state');
xlim([0.9*min(t_idx_list), max(t_idx_list)*1.1])


subplot(2,1,2);
plot([min(t_idx_list), max(t_idx_list)], [0,0], 'k-')
hold on;
plot(t_idx_list, fit - ooq_list, 'ro');
xlabel('Uncalibrated flight time [bins]');
ylabel('fit difference');
xlim([0.9*min(t_idx_list), max(t_idx_list)*1.1])

%% ===== TOF data on calibrated m/q axis =====
roi = t_index>=par(2);

moq1_r = 1./moq_calibrated(roi);
tof_r = tof_avg(roi);

figure;
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([0, 50])
xlabel('Charge state / mass of Xe^{131}');
ylabel('Ion yield [arb. units]');

grid on;


figure;
subplot(2,2,1);
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([4.5, 5.5])
grid on;

subplot(2,2,2);
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([7.5, 8.5])
grid on;

subplot(2,2,3);
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([11.5, 12.5])
grid on;

subplot(2,2,4);
plot(1./moq_calibrated(roi), tof_avg(roi), 'r');
xlim([32.5, 35.5])
grid on;



%% ===== calculate ratio between high and low =====
roi_low = moq1_r>1.44 & moq1_r<5.22;
roi_high = moq1_r>27.8 & moq1_r<34.35;

int_low = trapz(moq1_r(roi_low), tof_r(roi_low));
int_high = trapz(moq1_r(roi_high), tof_r(roi_high));

ratio = int_high / int_low;






%% ===== chamber position ratio scan =====
run = [195, 194, 188, 189, 190, 191, 192, 193];                     % run numbers (chamber position scan)
pos = [0.61, -1.425, -1.4, -3.24, -5.28, -7.22, -9.17, -11.21];     % corresponding chamber positions in [mm]
rat = [33.4, 35.8, 37.2, 40.85, 43.5, 44.2, 43.8, 40.2];            % ratios

figure;
plot(pos, rat, '-o')
xlabel('Chamber position [mm]');
ylabel('Ratio high/low charges states');

text(-5, 40, 'run 191')

