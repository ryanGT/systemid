from pylab import figure,show
from numpy import pi,zeros
from numpy.random import normal
import systemid
reload(systemid)
from systemid import Model,fit_time,fit_freq
from systemid.data import multiple_data
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
dt = .01
cush = 0.1
t = create_swept_sine_t(T, dt, cush)
maxf = 10.0
u = create_swept_sine_input(T, dt, maxf, deadtime=cush)
y = tf.lsim(u,t)
ymat = zeros((y.shape[0],5))
umat = zeros((u.shape[0],5))
for n in range(5):
    noise = normal(0,.001,len(u))
    ymat[:,n] = y+noise
    umat[:,n] = u

###################################################
# start systemid
g = 1.
z = .6
wn = 2*pi*8
num_dict = {'0':'g*wn**2'}
den_dict = {'2':'1','1':'2*z*wn','0':'wn**2'}
var_dict = {'g':g,'z':z,'wn':wn}
to_opt_dict = {'g':g,'z':z,'wn':wn}

data = multiple_data(t,umat,ymat)
#data.resample(2)
#data.scale_t(1.0/250)
#data.scale_output(1.0/128/4*2*pi)

model = Model(num_dict,den_dict,var_dict,to_opt_dict)

data.calc_coherence()

opt_dict = fit_time(model,data)
opt_model = Model(num_dict,den_dict,opt_dict)


# Time Data Stuff

fig = figure(1)

model.plot_resp(data.t,data.input,fig=fig,clear=True,title='Model vs. Exp',linelabel='Initial Guess')
opt_model.plot_resp(data.t,data.input,fig=fig,clear=False,linelabel='Optimized Model',linestyle=':',linewidth=3)
data.plot_output(fig=fig,clear=False,linelabel='Data Output',linestyle='--',linewidth=3)
data.plot_input(fig=fig,clear=False,linelabel='Data Input',linestyle='-',linewidth=1)

# Frequency Data Stuff

freq_data = data.experimental_transferfunction()
#freq_data.trim_at_freq(10)

freq_opt_dict = fit_freq(model,freq_data)
opt_freq_model = Model(num_dict,den_dict,freq_opt_dict)

fig = figure(2)
model.plot_bode(freq_data.f,fig=fig,linelabel='Guess',linestyle='-')
opt_freq_model.plot_bode(freq_data.f,fig=fig,linelabel='Opt',linestyle='-')
freq_data.plot_bode(fig=fig,linelabel='Swept Freq Bode',linestyle='-')

# Coherence

fig = figure(3)
data.plot_coherence(fig=fig,linestyle='-')

show()
