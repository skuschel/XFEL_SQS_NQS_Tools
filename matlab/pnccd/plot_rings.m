function plot_rings(center,radius)
%     enter.y=(583+482-52)/2+gap_size/0.075/2;
%     center.x=(570+472-10)/2;
%     plot_rings(center,54)
%     xlim(center.x+[-150 150])
%     ylim(center.y+[-150 150])
alpha_ax=linspace(0,2*pi,360);
x_circ=radius*sin(alpha_ax);
y_circ=radius*cos(alpha_ax);
hold on
plot(center.x,center.y,'rx');

for ring_fac=0.2:0.2:3
    plot(center.x+x_circ*ring_fac,center.y+y_circ*ring_fac,'r');
    
end

end