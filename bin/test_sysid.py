import systemid
import controls
from numpy import arange

test_step = 'step.txt'
g = 10
p = 10

t = arange(0,5,.01)
f = systemid.data.t_to_f(t)
t2 = systemid.data.f_to_t(f)

num = [g*p]
den = [1,p,0]

oltf = controls.TransferFunction(num,den)
cltf = controls.Feedback(oltf)
