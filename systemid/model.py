from scipy.optimize import fmin
from numpy import array,asarray,arange
from controls import TransferFunction
import copy
import plotting
import data
from utils import *

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

def optimizer(model,data,opt_function,cost_function,**kwargs):
    print 'Guessed Variables'
    print_vars(model.opt_dict)
    c = model.opt_dict.values()
    if kwargs:
        model.calc_freq_data(data.f)
        initial_error = cost_function(model,data,kwargs)
    else:
        initial_error = cost_function(model,data)
    print 'Initial Error: %s'%(initial_error,)
    if kwargs:
        new_var_dict = fmin(opt_function,c,args=(model,data,cost_function,kwargs))
    else:
        new_var_dict = fmin(opt_function,c,args=(model,data,cost_function))
    optimized_dict = var_dict_w_new_values(new_var_dict,model)
    opt_model = model.copy(var_dict=optimized_dict)
    if kwargs:
        opt_model.calc_freq_data(data.f)
        final_error = cost_function(opt_model,data,kwargs)
    else:
        final_error = cost_function(opt_model,data)
    print 'Final Error: %s'%(final_error,)
    print 'Optimized Variables'
    print_vars(optimized_dict)
    return optimized_dict


def fit_time_cost(model,data):
    model_output = do_lsim(model,data.input,data.t)
    data_output = data.output
    return sum((model_output-data_output)**2)

def fit_time_opt(c,model,data,cost_function):
    new_var_dict = var_dict_w_new_values(c,model)
    new_model = model.copy(var_dict=new_var_dict)
    e = cost_function(new_model,data)
    return e

def fit_time(model,data,opt_function=fit_time_opt,cost_function=fit_time_cost):
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
    return optimizer(model,data,opt_function,cost_function)

def fit_freq_cost_phase(model,data):
    evect = (model.phase-data.phase)**2
    return sum(evect)

def fit_freq_cost_mag(model,data):
    evect = (model.dbM-data.dbM)**2
    return sum(evect)

def fit_freq_cost(model,data,kwargs):
    mag_evect = fit_freq_cost_mag(model,data)
    phase_evect = fit_freq_cost_phase(model,data)
    e = mag_evect+kwargs['phase_weight']*phase_evect
    return e

def fit_freq_opt(c,model,data,cost_function,kwargs):
    new_var_dict =  var_dict_w_new_values(c,model)
    new_model = model.copy(var_dict=new_var_dict)
    new_model.calc_freq_data(data.f)
    return cost_function(new_model,data,kwargs)

def fit_freq(model,data,opt_function=fit_freq_opt,cost_function=fit_freq_cost,**kwargs):
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
    def_kwargs = {'phase_weight':0.1}
    def_kwargs.update(kwargs)
    return optimizer(model,data,opt_function,cost_function,**def_kwargs)

def _new_model_from_two(model1,model2,new_num_str,new_den_str):
        new_opt_dict = model1.opt_dict.copy()
        new_opt_dict.update(model2.opt_dict)
        new_var_dict = model1.var_dict.copy()
        new_var_dict.update(model2.var_dict)
        return Model(new_num_str,new_den_str,new_var_dict,new_opt_dict,model1.myvar)

    
class Model(TransferFunction):
    def __init__(self,num_dict,den_dict,var_dict,opt_dict='all',myvar='s'):
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
        if type(num_dict) == type({}):
            self.num_dict = num_dict
            self.num_str = poly_dict_to_str(self.num_dict,myvar=myvar)
        elif type(num_dict) == type(''):
            self.num_str = num_dict 
            self.num_dict = PolyHasher(num_dict,var_dict,myvar=myvar)[1]
        if type(den_dict) == type({}):
            self.den_dict = den_dict
            self.den_str = poly_dict_to_str(self.den_dict,myvar=myvar)
        elif type(den_dict) == type(''):
            self.den_str = den_dict
            self.den_dict = PolyHasher(den_dict,var_dict,myvar=myvar)[1]
        self.var_dict = var_dict
        if opt_dict == False:
            self.opt_dict = opt_dict
        elif opt_dict == 'all':
            self.opt_dict = self.var_dict.copy()
        elif isinstance(opt_dict,dict):
            self.opt_dict = opt_dict
        num = exec_coeffs(self.num_dict,var_dict)
        den = exec_coeffs(self.den_dict,var_dict)
        TransferFunction.__init__(self,num,den)

    def __repr__(self, labelstr='systemid.Model'):
        return TransferFunction.__repr__(self,labelstr)

    def __add__(self,other):
        if isinstance(other,int) or isinstance(other,float):
            return Model(str(other)+'*('+self.den_str+')+'+self.num_str,\
                         self.den_str,self.var_dict,self.opt_dict,self.myvar)
        elif isinstance(other,Model):
            new_num_str = '('+self.num_str+')'+'*'+'('+other.den_str+')'+'+'+'('+self.den_str+')'+'*'+'('+other.num_str+')'
            new_den_str = '('+self.den_str+')'+'*'+'('+other.den_str+')'
            return _new_model_from_two(self,other,new_num_str,new_den_str)

    def __sub__(self,other):
        if isinstance(other,int) or isinstance(other,float):
            return Model(self.num_str+'-'+str(other)+'*('+self.den_str+')',\
                         self.den_str,self.var_dict,self.opt_dict,self.myvar)
        elif isinstance(other,Model):
            new_num_str = '('+self.num_str+')'+'*'+'('+other.den_str+')'+'-'+'('+self.den_str+')'+'*'+'('+other.num_str+')'
            new_den_str = '('+self.den_str+')'+'*'+'('+other.den_str+')'
            return _new_model_from_two(self,other,new_num_str,new_den_str)

    def __mul__(self,other):
        if isinstance(other,int) or isinstance(other,float):
            return Model(str(other)+'*('+self.num_str+')',\
                         self.den_str,self.var_dict,self.opt_dict,self.myvar)
        elif isinstance(other,Model):
            new_num_str = '('+self.num_str+')*('+other.num_str+')'
            new_den_str = '('+self.den_str+')*('+other.den_str+')'
            return _new_model_from_two(self,other,new_num_str,new_den_str)

    def __div__(self,other):
        if isinstance(other,int) or isinstance(other,float):
            return Model(self.num_str+'/'+str(other),\
                         self.den_str,self.var_dict,self.opt_dict,self.myvar)
        elif isinstance(other,Model):
            new_num_str = '('+self.num_str+')*('+other.den_str+')'
            new_den_str = '('+self.den_str+')*('+other.num_str+')'
            return _new_model_from_two(self,other,new_num_str,new_den_str)

    def copy(self,**kwargs):
        new_dict = copy.copy(self.__dict__)
        new_dict.update(kwargs)
        new = Model(new_dict['num_dict'],new_dict['den_dict'],\
                    new_dict['var_dict'],new_dict['opt_dict'],new_dict['myvar'])
        return new

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

    def calc_freq_data(self,f):
        self.f = to_array(f)
        self.spectrum = self.FreqResp(f,fignum=None)
        self.freq_data = data.frequency_data(f,self.spectrum)
        self.dbM = self.freq_data.dbM
        self.phase = self.freq_data.phase

    def plot_bode(self,**plot_options):
        return self.freq_data.plot_bode(**plot_options)
        
