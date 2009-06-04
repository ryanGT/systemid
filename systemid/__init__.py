from scipy.optimize import fmin
from numpy import array,asarray,arange
from controls import TransferFunction
import data,plotting,utils
from utils import *
from testing import test

__all__ = ['data','plotting','utils','testing']

def do_lsim(tf,input,t):
    '''
    Linear simulation of LTI system.  

    Parameters
    ----------
    tf : Instance of `controls.Transferfunction` or `scipy.signal.ltisys.lti`
    input : array or list
            Input to the LTI system.
    t : array or list
        Time vector corresponding to the input.

    Returns
    -------
    out: array
         Ouput of the linear simulation of `tf`.
    '''
    if hasattr(tf,'lsim'):
        try:
            out =  tf.lsim(input, t)
        except:
            out =  tf.lsim2(input,t)
    else:
        try:
            out = signal.lsim(tf,input,t)[1]
        except:
            out = signal.lsim2(tf,input,t)[1]
    return out

def print_vars(var_dict):
    '''
    Print variables in `var_dict` in the format '`key` = `value`'.

    Parameters
    ----------
    var_dict : dictionary
               The keys are strings representing a variable and the
               values are the value of the variable.  Similar to a
               namespace.
               
    Returns
    -------
    None
    '''
    for k,v in var_dict.items():
        if k != '__builtins__':
            print k+' = ',v

def fit_time(model,time_data):
    '''
    Optimizes the parameters of `model` to `time_data` using
    `scipy.optimize.fmin` and a sum of difference of squares
    cost function.
    
    Parameters
    ----------
    model : instance of `Model`
    data  : instance of a `time_data*` 
            Experimental data from system of `model` is
            a model of (see data.py).
            
    Returns
    -------
    optimized_dict : dictionary
           A dictionary with strings representing the parameters
           of `model` and their optimized values as keys.
           {'A':<A's optimized value>:,'p':<p's optimized value>}
       '''
    def opt(c,opt_lst,var_dict,num_dict,den_dict,initial_error):
        num,den,odict = OptNumDen(c,opt_lst,var_dict,num_dict,den_dict)
        tf = TransferFunction(num,den)
        outputm = do_lsim(tf,time_data.input,time_data.t)
        e = sum((time_data.output-outputm)**2)
        return e
    tf = TransferFunction(model.num,model.den)
    initial_error = sum((do_lsim(tf,time_data.input,time_data.t)-time_data.output)**2)
    print 'Initial Error: %s'%(initial_error,)
    c = model.opt_dict.values()
    opt_lst = model.opt_dict.keys()
    cn = fmin(opt,c,args=(opt_lst,model.var_dict,model.num_dict,model.den_dict,initial_error))
    num,den,optimized_dict = OptNumDen(cn,opt_lst,model.var_dict,model.num_dict,model.den_dict)
    tf = TransferFunction(num,den)
    final_error = sum((do_lsim(tf,time_data.input,time_data.t)-time_data.output)**2)
    print 'Final Error: %s'%(final_error,)
    print 'Optimized Variables'
    print_vars(optimized_dict)
    return optimized_dict

def fit_freq(model,freq_data):
    '''
    Optimizes the parameters of `model` to `freq_data` using
    `scipy.optimize.fmin` and a sum of difference of squares
    cost function.
    
    Parameters
    ----------
    model : instance of `Model`
    data  : instance of a `frequency_data*` 
            FFT of sinusoidal experimental data from system `model` is
            a model of (see data.py).
            
    Returns
    -------
    optimized_dict : dictionary
           A dictionary with strings representing the parameters
           of `model` and their optimized values as keys.
           {'A':<A's optimized value>:,'p':<p's optimized value>}
       '''
    def opt(c,opt_lst,var_dict,num_dict,den_dict):
        num,den,odict = OptNumDen(c,opt_lst,var_dict,num_dict,den_dict)
        outputm = TransferFunction(num,den).FreqResp(freq_data.f,fignum=None)
        spectrum = freq_data.spectrum
        if not hasattr(outputm,'__len__'):
            outputm = [outputm]
        outputm = asarray(outputm)
        for n,c,d in zip(range(len(outputm)),outputm,freq_data.spectrum):
            try:
                
                x = c-d#len(c)
            except:
                #print 'found outputm'
                print n
                print c,d
            #try:
            #    len(d)
            #except:
            #    print 'found spec'
            #    print d
        #print type(outputm)
        #print type(freq_data.spectrum)
        #for c in outputm:
        #    if 
        #print freq_data.spectrum[0]
        #print freq_data.spectrum[0]-outputm[0]
        if abs(len(spectrum)-len(outputm))==1:
            if len(spectrum)>len(outputm):
                spectrum = spectrum[:-1]
            else:
                outputm = outputm[:-1]
        e = spectrum-outputm
        e = e**2
        e = sum(e)
        return e
    if not hasattr(freq_data.f,'__len__'):
        freq_data.f = [freq_data.f]
    if not hasattr(freq_data.spectrum,'__len__'):
        freq_data.spectrum = [freq_data.spectrum]
    freq_data.f = asarray(freq_data.f)
    freq_data.spectrum = asarray(freq_data.spectrum)
    c = model.opt_dict.values()
    opt_lst = model.opt_dict.keys()
    cn = fmin(opt,c,args=(opt_lst,model.var_dict,model.num_dict,model.den_dict))
    num,den,optimized_dict = OptNumDen(cn,opt_lst,model.var_dict,model.num_dict,model.den_dict)
    print 'Optimized Variables'
    print_vars(optimized_dict)
    return optimized_dict

class Model(TransferFunction):
    def __init__(self,num_dict,den_dict,var_dict,opt_dict=False):
        '''
        Class to represent a model of a linear time invariant
        dynamical system.

        Parameters
        ----------
        opt_dict : dictionary
                   Represent the parameters of `num_dict` and `den_dict`
                   that can be optimized and their initial values.
                   {'A':10,'p':10}
        var_dict : dictionary
                   Represents all parameters of `num` and `den`.
                   {'A':10,'p':10}
        num_dict : dictionary
                   Represents numerator.  Keys are the power of the
                   polynomial variable and values are a string of the
                   symbolic form of the coefficient. {'0':'A*p'}
        den_dict : dictionary
                   Represents denominator. Similar to `num_dict`.
                   {'1':'1','0':p}
        input : array
                Input to the system.
        '''
        self.num_dict = num_dict
        self.den_dict = den_dict
        self.var_dict = var_dict
        if opt_dict:
            self.opt_dict = opt_dict
        num = exec_coeffs(num_dict,var_dict)
        den = exec_coeffs(den_dict,var_dict)
        TransferFunction.__init__(self,num,den)

    def __repr__(self, labelstr='systemid.Model'):
        return TransferFunction.__repr__(self,labelstr)

    def __add__(self,other):
        #
        # This is a little more complicated than
        # I initially anticipated. Because I need
        # to somehow recreate num_dict and den_dict
        # Maybe use sympy?
        #
        #added = TransferFunction.__add__(self,other)
        #return Model(self.num_)
        pass

    def plot_resp(self,t,input,**plot_options):
        '''
        Plot the the response to `input` the system the `Model` instance
        is representing.

        Parameters
        ----------
        t : array
        input : array
        kwargs : dictionary
                 Keyword arguments for `plotting.plot_time`
                 (see plotting.py)
        '''
        y = do_lsim(self,input,t)
        fig = plotting.plot_time(t,y,**plot_options)
        return fig

    def plot_bode(self,f,**plot_options):
        if not hasattr(f,'__len__'):
            f = [f]
        f = asarray(f)
        tf = TransferFunction(self.num,self.den)
        comp = tf.FreqResp(f, fignum=None)
        model = data.frequency_data(f,comp)
        return model.plot_bode(**plot_options)
        
