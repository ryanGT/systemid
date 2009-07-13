from systemid.testing.pytest import raises
from pylab import figure
import systemid.data as data
import os
t_dir = os.path.split(__file__)[0]

step = os.path.join(t_dir,'step.txt')
fixed = os.path.join(t_dir,'fixed.txt')
fixed_sine_freq = 5.
swept = 'swept.txt'
usecols = (0,2,4)
A =  20
p =  200
num_dict = {'0':'A*p'}
den_dict = {'2':'1','1':'p','0':'A*p'}
var_dict = {'A':A,'p':p}
to_opt_dict = {'A':A,'p':p}
skiprows = 3

def test_time_data_as_step():
    step_d = data.time_data_file(step)
    step_d.read(usecols,skiprows=skiprows)
    u = step_d.input
    y = step_d.output
    u = u*5.0
    y = y*5.0
    step_d.scale_input(5.0)
    assert step_d.input.all() == u.all()
    assert step_d.output.all() == y.all()

def test_time_data_as_fixed():
    d = data.time_data_file(fixed)
    d.read(usecols,skiprows=3)
    fig = figure(1)
    d.plot_input(fig=fig,clear=False,linelabel='Data Input')
    d.plot_output(fig=fig,clear=False,linelabel='Data Output')
    freq_data = d.experimental_transferfunction(fixed_sine_freq)
    fig = figure(2)
    freq_data.plot_bode(fig=fig,linelabel='Fixed Freq Bode')
