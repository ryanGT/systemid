from systemid.data import time_data_file
from systemid import Model,fit_time,fit_freq
from pylab import figure,show
from numpy import pi,argmax
from controls import feedback

#a comment
#another comment
A =  10
p =  12
A =  20
p =  200

num_dict = {'0':'A*p'}
den_dict = {'2':'1','1':'p','0':'A*p'}
var_dict = {'A':A,'p':p}
to_opt_dict = {'A':A,'p':p}

usecols = (0,2,4)
fixed_sine_freq = 5.
datafile = 'fixed.txt'

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

freq_data = data.experimental_transferfunction(fixed_sine_freq)

freq_opt_dict = fit_freq(model,freq_data)
opt_freq_model = Model(num_dict,den_dict,freq_opt_dict)

fig = figure(2)
model.plot_bode(fixed_sine_freq,fig=fig,linelabel='Guess')
opt_freq_model.plot_bode(fixed_sine_freq,fig=fig,linelabel='Opt')
freq_data.plot_bode(fig=fig,linelabel='Fixed Freq Bode')

show()
