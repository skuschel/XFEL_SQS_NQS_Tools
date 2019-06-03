import time


class performanceMonitor():
    def __init__(self,trainStep=1):
        self.t_start = time.time()
        self.t_start_loop = self.t_start
        self.for_loop_step_dur = 0
        self.n=-1
        self.freq_avg = 0
        self.dt_avg = 0
        self.trainId = 0
        self.trainId_old = -1
        self.skip_count = 0
        self.trainStep = trainStep

    def iteration(self):
        self.n+=1
        self.dt = (time.time()-self.t_start)
        self.t_start = time.time()
        freq = 1/self.dt
        if self.n>0:
            self.dt_avg = (self.dt_avg * (self.n-1) + self.dt) / self.n
            freq_avg = 1/self.dt_avg
            loop_classification_percent = self.for_loop_step_dur/0.1*100
            if loop_classification_percent < 100:
                loop_classification_msg="OK"
            else:
                loop_classification_msg="TOO LONG!!!"
            print("Frequency: "+str(round(freq_avg,1)) +" Hz  |  skipped: "+str(self.skip_count)+" ( "+str(round(self.skip_count/self.n*100,1))+" %)  |  n: "+str(self.n)+"/"+str(self.trainId)+"  |  Loop benchmark: "+str(round(loop_classification_percent,1))+ " % (OK if <100%) - "+loop_classification_msg)
        self.t_start_loop = time.time()

    def update_trainId(self,tid):
        self.trainId_old = self.trainId
        self.trainId = tid
        if self.n == 0:
            self.trainId_old = str(int(tid) -1)
        if int(self.trainId) - int(self.trainId_old) is not self.trainStep:
            self.skip_count +=1

    def time_for_loop_step(self):
        self.for_loop_step_dur = time.time()-self.t_start_loop



# Helper to convert from holoviews to bokeh
def hv_to_bokeh_obj(hv_layout,renderer):
    # convert holoviews layout to bokeh object
    hv_plot = renderer.get_plot(hv_layout)
    return hv_plot.state
