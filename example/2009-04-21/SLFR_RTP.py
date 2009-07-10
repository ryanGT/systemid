from pylab import *
from scipy import *

import controls
reload(controls)

#import PSoC_serial_v_2_0 as PS
#reload(PS)

import pylab_util

import serial, sys, time

from rwkos import amiLinux

from IPython.Debugger import Pdb

dstr = 'int32'

import Real_Time_Python
reload(Real_Time_Python)


class OL_Test(Real_Time_Python.Motor_OL_Test):
    def __init__(self, stopn=1000, mysat=200, fd=500.0, dstr='int32', \
                 num_cols=3):
        Real_Time_Python.Motor_OL_Test.__init__(self, stopn=stopn, mysat=mysat,  \
                                                fd=fd, dstr=dstr, num_cols=num_cols)
        self.legend = ['u','v','$\\theta$','a']
        self.save_vars = ['u','v','y','a']

    def header(self):
        mylist = ['#SLFR RTP OL_Test']
        return mylist
        
    def Save(self, filepath, fmt='%0.10g', delim='\t'):
        t = self.nvect*self.dt
        data_list = [t, self.nvect]
        for item in self.save_vars:
            curvect = getattr(self, item+'vect')
            data_list.append(curvect)
        self.save_data = column_stack(data_list)
        self.save_labels = ['t','n']+self.legend
        f = open(filepath, 'wb')
        label_row = '#'+delim.join(self.save_labels)+'\n'
        myheader = self.header()
        outheader = []
        for line in myheader:
            if line[-1] != '\n':
                line += '\n'
            outheader.append(line)
        f.writelines(outheader)
        f.write(label_row)
        savetxt(f, self.save_data, fmt=fmt, delimiter=delim)
        
    def Plot(self, fi=1, clear=True):
        self.plot_data = column_stack([self.uvect, self.vvect, \
                                       self.yvect, self.avect])
        pmax = self.plot_data.max()
        pmin = self.plot_data.min()
        ylim = [pmin-5, pmax+5]
        pylab_util.plot_cols(self.nvect, self.plot_data, fi=fi, \
                             leg=self.legend, clear=clear, ylim=ylim)
        show()


    def _initialize_data_vectors(self, uvect):
        self.uvect = uvect
        self.stopn = len(uvect)

        #self.raw_data = zeros((self.stopn, 2*self.num_cols), dtype=self.dstr)

        self.nvect = zeros((self.stopn,), dtype=self.dstr)
        self.yvect = zeros((self.stopn,), dtype=self.dstr)
        self.vvect = zeros((self.stopn,), dtype=self.dstr)
        self.avect = zeros((self.stopn,), dtype=self.dstr)
    
    def _Run_Test(self, uvect):
        self._open_ser()
        self.flush_ser()

        self.Get_IC()
        #self.yvect[0] = self.IC

        for i in range(self.stopn):
            self.nvect[i] = self.Read_Two_Bytes_Twos_Comp()
            self.yvect[i] = self.Read_Two_Bytes_Twos_Comp()
            self.avect[i] = self.Read_Two_Bytes_Twos_Comp()

            self.WriteByte(47)
            cur_v = self.calc_v(i)
            #my_pause(300)
            self.WriteInt(cur_v)

    def Run_Test(self, uvect, plot=True, fi=1, clear=True, initialize=True):
        if initialize:
            self._initialize_data_vectors(uvect)
        self._Run_Test(uvect)
        self.Send_One_Voltage(v=0)
        self.Stop_PSoC_ser()
        self.Close_Serial()
        if plot:
            self.Plot(fi=fi, clear=clear)
        return self.nvect, self.yvect

class P_control_Test(OL_Test):
    def __init__(self, kp=1, **kwargs):
        OL_Test.__init__(self, **kwargs)
        self.kp = kp


    def header(self):
        mylist = ['#SLFR RTP P_control_Test']
        mylist.append('#kp=%s'%self.kp)
        return mylist
        
    
    def Run_Test(self, uvect, **kwargs):
        self.evect = zeros((len(uvect),), dtype=self.dstr)
        return OL_Test.Run_Test(self, uvect, **kwargs)
        

    def calc_v(self, i):
        self.evect[i] = self.uvect[i] - self.yvect[i]
        self.vvect[i] = self.sat(self.evect[i]*self.kp)
        return self.vvect[i]


class Motor_Comp(OL_Test):
    def __init__(self, b0, b1, a1, gain=1.0, **kwargs):
        OL_Test.__init__(self, **kwargs)
        self.b0 = b0
        self.b1 = b1
        self.a1 = a1
        self.gain = gain
        
    def header(self):
        mylist = ['#SLFR RTP Motor_Comp']
        mylist.append('#b0=%s'%self.b0)
        mylist.append('#b1=%s'%self.b1)
        mylist.append('#a1=%s'%self.a1)
        return mylist
        
        
    def Run_Test(self, uvect, **kwargs):
        self.evect = zeros((len(uvect),), dtype=self.dstr)
        return OL_Test.Run_Test(self, uvect, **kwargs)


    def calc_v(self, i):
        self.evect[i] = self.uvect[i] - self.yvect[i]
        if i > 0:
            vtemp = (self.evect[i]*self.b0+self.evect[i-1]*self.b1)*self.gain-self.vvect[i-1]*self.a1
        else:
            vtemp = self.evect[i]*self.b0#force all initial conditions to be zero
        self.vvect[i] = self.sat(vtemp)
        return self.vvect[i]



class Motor_Comp_w_accel_fb(OL_Test):
    def __init__(self, Gth, Ga=None, \
                 dt=1.0/500.0, **kwargs):
        OL_Test.__init__(self, **kwargs)
        self.Gth = Gth
        self.Ga = Ga
        self.dt = dt
        self.Gth_num, self.Gth_den = self.Gth.c2d_tustin(dt=self.dt)
        self.Gth_z = controls.Digital_Compensator(self.Gth_num, self.Gth_den)
        if Ga is not None:
            self.Ga_num, self.Ga_den = self.Ga.c2d_tustin(dt=self.dt)
            self.Ga_z = controls.Digital_Compensator(self.Ga_num, self.Ga_den)
            self.use_accel_fb = True
            print('setting use_accel_fb to True')
        else:
            self.Ga_num = []
            self.Ga_den = []
            self.use_accel_fb = False
        
        
    def header(self):
        mylist = ['#SLFR RTP Motor_Comp_w_accel_fb']
        mylist.append('#Gth num=%s'%self.Gth_num)
        mylist.append('#Gth den=%s'%self.Gth_den)
        mylist.append('#Ga num=%s'%self.Ga_num)
        mylist.append('#Ga den=%s'%self.Ga_den)
        return mylist
        
        
    def Run_Test(self, uvect, **kwargs):
        print('running the Run_Test method of Motor_Comp_w_accel_fb')
        self.evect = zeros((len(uvect),), dtype=self.dstr)
        self.thd_hat_vect = zeros((len(uvect),), dtype=self.dstr)
        self.vavect = zeros((len(uvect),), dtype=self.dstr)
        self._initialize_data_vectors(uvect)
        self.Gth_z.input = self.evect
        self.Gth_z.output = self.vvect
        if self.use_accel_fb:
            self.Ga_z.input = self.avect
            self.Ga_z.output = self.vavect
        return OL_Test.Run_Test(self, uvect, initialize=False, **kwargs)


    def calc_v(self, i):
        if self.use_accel_fb:
            #accel feedback forms an outer loop that affects the input to the theta control feedback loop
            self.vavect[i] = self.Ga_z.calc_out(i)
            thd = self.uvect[i] - self.vavect[i]
        else:
            thd = self.uvect[i]
        self.thd_hat_vect[i] = thd
        self.evect[i] = thd - self.yvect[i]
        vtemp = self.Gth_z.calc_out(i)
        self.vvect[i] = self.sat(vtemp)
        return self.vvect[i]

