from pylab import figure,show
from scipy import pi

import systemid
reload(systemid)
from systemid import Model,fit_time
from systemid.data import time_data_file,time_data
del systemid


############################
# Try 1
A =  125
p =  125
z =  7.
B = 5


#A =  5.73652650061
#p =  5.55759474336
#B =  7.95846529359
#z =  4.19003365228

#A =  97385.3465539
#p =  7636.27078234
#c =  94820.4963045
#z =  54.3639192917

num_dict = {'0':'A'}
den_dict = {'2':'1','1':'z','0':'p'}
var_dict = {'A':A,'p':p,'z':z,'B':B}
to_opt_dict = {'A':A,'p':p,'z':z,'B':B}
############################

usecols = (0,2,4)

datafile = 'step.txt'

data = time_data_file(datafile)
data.read(usecols,skiprows=3)
#data.resample(2)
#data.scale_t(1.0/250)
#data.scale_output(1.0/128/4*2*pi)

##############################
# remove steady state stuff

inds = data.t<.7
new_data = time_data(data.t[inds],data.input[inds],data.output[inds])

###############################

model = Model(num_dict,den_dict,var_dict,to_opt_dict)

opt_dict = fit_time(model,new_data)
opt_model = Model(num_dict,den_dict,opt_dict)

fig = figure(1)
model.plot_resp(new_data.t,new_data.input,fig=fig,clear=True,linelabel='Initial Guess')
opt_model.plot_resp(new_data.t,new_data.input,fig=fig,clear=False,title='Model vs. Exp',linelabel='Opt')
new_data.plot_output(fig=fig,clear=False,linelabel='Output')
new_data.plot_input(fig=fig,clear=False,linelabel='Input')

show()
