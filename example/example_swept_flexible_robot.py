from systemid.data import time_data_file
from systemid import Model,fit_time,fit_freq
from pylab import figure,show
from numpy import pi,argmax
from controls import feedback

A =  1000#1154.96979228
p =  40#44.3884892509
z =  .5#0.8318682051
num_dict = {'0':'A'}
den_dict = {'2':'1','1':'z*p','0':'p**2'}
var_dict = {'A':A,'p':p,'z':z}
to_opt_dict = {'A':A,'p':p,'z':z}

usecols = (0,2,4)
datafile = 'swept.txt'

data = time_data_file(datafile)
data.read(usecols,skiprows=3)
#data.resample(2)
#data.scale_t(1.0/250)
#data.scale_output(1.0/128/4*2*pi)

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

#freq_opt_dict = fit_freq(model,freq_data)
#opt_freq_model = Model(num_dict,den_dict,freq_opt_dict)

fig = figure(2)
model.plot_bode(freq_data.f,fig=fig,linelabel='Guess')
#opt_freq_model.plot_bode(freq_data.f,fig=fig,linelabel='Opt')
freq_data.plot_bode(fig=fig,linelabel='Swept Freq Bode')

show()
