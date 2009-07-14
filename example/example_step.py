from pylab import figure,show
from scipy import pi

import systemid
reload(systemid)
from systemid import Model,fit_time
from systemid.data import time_data
del systemid
from controls import TransferFunction,create_step_vector
from numpy import arange

# theorectical system parameters
wn = 10.0*2*pi
z = .7
g = 2.0
num = [g*wn**2]
den = [1,2*z*wn,wn**2]

# create some data
tf = TransferFunction(num,den)
t = arange(0,2,.01)
u = create_step_vector(t, step_time=.5, amp=1.0)
y = tf.lsim(u,t)

#################################################
# start systemid
num_dict = {'0':'g*wn**2'}
den_dict = {'2':'1','1':'2*z*wn','0':'wn**2'}
var_dict = {'g':1,'z':z,'wn':10}
to_opt_dict = {'g':5,'z':z,'wn':10}

data = time_data(t,u,y)

###############################

model = Model(num_dict,den_dict,var_dict,to_opt_dict)

opt_dict = fit_time(model,data)
opt_model = Model(num_dict,den_dict,opt_dict)

fig = figure(1)
model.plot_resp(data.t,data.input,fig=fig,clear=True,linelabel='Initial Guess')
opt_model.plot_resp(data.t,data.input,fig=fig,clear=False,title='Model vs. Exp',linelabel='Opt',linewidth=5,linestyle=':')
data.plot_output(fig=fig,clear=False,linelabel='Output',linestyle='--')
data.plot_input(fig=fig,clear=False,linelabel='Input',linestyle='-',linewidth=1)

show()
