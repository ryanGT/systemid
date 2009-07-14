from pylab import figure,show
from scipy import pi

import systemid
reload(systemid)
from systemid import Model,fit_time,fit_freq
from systemid.data import time_data
del systemid
from controls import TransferFunction,create_swept_sine_t,create_swept_sine_input


# theorectical system parameters
wn = 10.0*2*pi
z = .7
g = 2.0
num = [g*wn**2]
den = [1,2*z*wn,wn**2]

# create some data
tf = TransferFunction(num,den)
T = 1.0
dt = 1.0/1000.0
cush = 0.1
t = create_swept_sine_t(T, dt, cush)
maxf = 20.0
u = create_swept_sine_input(T, dt, maxf, deadtime=cush)
y = tf.lsim(u,t)

# start systemid
num_dict = {'0':'g*wn**2'}
den_dict = {'2':'1','1':'2*z*wn','0':'wn**2'}
var_dict = {'g':5,'z':z,'wn':10}
to_opt_dict = {'g':5,'z':z,'wn':10}

data = time_data(t,u,y)

###############################

model = Model(num_dict,den_dict,var_dict,to_opt_dict)

opt_dict = fit_time(model,data)
opt_model = Model(num_dict,den_dict,opt_dict)


# Time Data Stuff

fig = figure(1)

model.plot_resp(data.t,data.input,fig=fig,clear=True,title='Model vs. Exp',linelabel='Initial Guess')
opt_model.plot_resp(data.t,data.input,fig=fig,clear=False,linelabel='Optimized Model')
data.plot_input(fig=fig,clear=False,linelabel='Data Input')
data.plot_output(fig=fig,clear=False,linelabel='Data Output')

# Frequency Data Stuff

freq_data = data.experimental_transferfunction()

freq_opt_dict = fit_freq(model,freq_data)
opt_freq_model = Model(num_dict,den_dict,freq_opt_dict)

fig = figure(2)
model.plot_bode(freq_data.f,fig=fig,linelabel='Guess')
opt_freq_model.plot_bode(freq_data.f,fig=fig,linelabel='Opt',linestyle='-')
freq_data.plot_bode(fig=fig,linelabel='Swept Freq Bode',line_style='-')

show()
