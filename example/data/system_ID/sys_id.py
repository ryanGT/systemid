from pylab import *
from scipy import *

import controls


def loadstep(filename):
    data = loadtxt(filename, skiprows=1)
    n = data[:,0]
    v = data[:,1]
    th = data[:,2]
    return n, v, th


testnums = range(3,9)

pat = 'step%d.txt'

figure(1)
clf()

figure(2)
clf()

dt = 1.0/250

firstfile = pat % testnums[0]
n, v, th = loadstep(firstfile)
t = n*dt

thmat = zeros((th.shape[0], len(testnums)))

for j, ind in enumerate(testnums):
    filename = pat % ind
    n, v, th = loadstep(filename)

    thmat[:,j] = th
    
    figure(1)
    plot(t, th)
    figure(2)
    plot(t, v)

thave = thmat.mean(axis=1)

figure(1)
plot(t, thave, 'k-')

A = 1200.0
p = 3.0

figure(3)
clf()
plot(t, thave, 'ks')

tf = controls.TransferFunction(A*p,[1,p,0])
tf.step_response(dt=t[1], maxt=t.max(), fignum=3, clear=False)

def mymodel(c):
    A = c[0]
    p = c[1]
    m = exp(-p*t)*A/p+t*A-A/p
    return m

def mycost(c):
    model = mymodel(c)
    evect = thave-model
    return sum(evect**2)

cf = optimize.fmin(mycost, [A,p])
    
#plot(t,om)

#modelf = mymodel(cf)
#plot(t, modelf, 'r-', linewidth=2.0)

Af = cf[0]
pf = cf[1]
G = controls.TransferFunction(Af*pf,[1,pf,0])
G.step_response(fignum=3, clear=False, dt=t[1], maxt=t.max(), linewidth=2.0, color='r')

figure(1)
leglist = [str(item) for item in testnums]
legend(leglist+['ave'],2)

figure(3)
legend(['ave data','guess','fmin result'],2)

figure(2)
legend(leglist, 4)

filenames = ['step_response_data','step_inputs','fmin_fit']

for ind, filename in zip(range(1,4), filenames):
    figure(ind)
    xlabel('Time (sec)')
    if ind == 2:
        ylabel('Step Input Voltage')
    else:
        ylabel('Step Response')
    savefig(filename+'.png')


show()
