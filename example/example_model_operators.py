from numpy import pi
from systemid import *

num1 = 'w1**2*s**2'
num2 = 'w2**2*s**2'
den1 = 's**2+2*z*w1*s+w1**2'
den2 = 's**2+2*z*w2*s+w2**2'
var_dict1 = {'z':.7,'w1':2*pi*10}
var_dict2 = {'z':.5,'w2':2*pi*15}

m1 = Model(num1,den1,var_dict1,'all')
m2 = Model(num2,den2,var_dict2,'all')

m3 = m1+m2
m3 = m1-m2
m3 = m1*m2
m3 = m1/m2
m3 = m1+5
m3 = m1-5
m3 = m1*5
m3 = m1/5

