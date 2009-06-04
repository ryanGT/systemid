from pylab import *
from scipy import *
import controls
import SLFR_RTP
class Motor_CompMod(SLFR_RTP.OL_Test):
    def __init__(self,c,a, cgain=1.0,again=1.0, **kwargs):
        SLFR_RTP.OL_Test.__init__(self, **kwargs)
        self.cb0 = c[0][0]
        self.cb1 = c[0][1]
        self.ca1 = c[1][1]
        self.cgain = cgain
        self.ab0 = a[0][0]
        self.ab1 = a[0][1]
        self.ab2 = a[0][2]
        self.ab3 = a[0][3]
        self.aa0 = a[1][0]
        self.aa1 = a[1][1]
        self.aa2 = a[1][2]
        self.aa3=a[1][3]
        self.again = again
        
    #def header(self):
    #    mylist = ['#SLFR RTP Motor_Comp']
    #    mylist.append('#b0=%s'%self.b0)
    #    mylist.append('#b1=%s'%self.b1)
    #    mylist.append('#a1=%s'%self.a1)
    #    return mylist
        
        
    def Run_Test(self, uvect, **kwargs):
        self.evect = zeros((len(uvect),), dtype=self.dstr)
        self.Vvect=self.evect[:]
        return SLFR_RTP.OL_Test.Run_Test(self, uvect, **kwargs)


    def calc_v(self, i):
        self.evect[i] = self.uvect[i] - self.yvect[i]
        if i > 0:
            vtemp = (self.evect[i]*self.cb0+self.evect[i-1]*self.cb1)*self.cgain-self.vvect[i-1]*self.ca1
        else:
            vtemp = self.evect[i]*self.cb0#force all initial conditions to be zero
        vtemp_other=self.calc_v2(i)
        vtemp=vtemp+vtemp_other
        self.vvect[i] = self.sat(vtemp)
        return self.vvect[i]
	
    def calc_v2(self,i):
        return 0
        if i >=3:
            vtemp = (self.avect[i]*self.ab0+self.avect[i-1]*self.ab1+self.avect[i-2]*self.ab2+self.avect[i-3]*self.ab3)
            vtemp=vtemp*self.again-self.Vvect[i-1]*self.aa1-self.Vvect[i-2]*self.aa2-self.Vvect[i-3]*self.aa3
        else:
            if i==0:
                vtemp = self.avect[i]*self.ab0#force all initial conditions to be zero
            if i==1:
                vtemp = (self.avect[i]*self.ab0+self.avect[i-1]*self.ab1)
                vtemp=vtemp*self.again-self.Vvect[i-1]*self.aa1
            if i==2:
                vtemp = (self.avect[i]*self.ab0+self.avect[i-1]*self.ab1+self.avect[i-2]*self.ab2)
                vtemp=vtemp*self.again-self.Vvect[i-1]*self.aa1-self.Vvect[i-2]*self.aa2	
        vvect = self.sat(vtemp)
        return vvect
fd = 500.0
dt = 1.0/fd

Gc=3.0*controls.TransferFunction([1.0,13.0],[1.0,20.0])
GLP=1600.0*controls.TransferFunction([1.0],[1.0,56.0,1600.0])
GPI=-1.0*controls.TransferFunction([1.0,20.0],[1.0,0.0])
Ga=GLP*GPI

cb,ca=Gc.c2d_tustin(dt=dt)
ab,aa=Ga.c2d_tustin(dt=dt)
c=[cb,ca]
a=[ab,aa]
print 'C'
print 'b='+str(cb)
print 'a='+str(ca)
print 'A'
print 'b='+str(ab)
print 'a='+str(aa)

MC = Motor_CompMod(c=c, a=a, cgain=1.0,again=1.0)
MC.Reset_Theta()#set encoder value to 0
MC.Close_Serial()
#use this command to give a step input to the joint
#MC.Step_Response(amp=500, stopn=1000)


show()

