import re,sympy
import systemid
from systemid.utils import OptNumDen


def HashStaticVariables(static_str):
    '''
    Split `static_str` by | or , to make a list.

    Parameters
    ----------
    static_str : str

    Returns
    -------
    static_lst : list
    '''
    var_splitter = re.compile('\||,')
    return var_splitter.split(static_str)

def VariableStrHasher(varstr):
    '''
    Parse a string such as 'A:100|p:10' and turn it
    into a dictionary with keys ['A','p'] and values
    [100,10]. varstr will probably come from a wx.TexCtrl.
    In this case the returned dictionary would be
    {'p':10,'A':100}

    Parameters
    ----------
    varstr : string

    Returns
    -------
    vardict : dictionary
       '''
    first = re.compile('\||,') 
    second = re.compile(':|=')
    split1 = first.split(varstr) #'A:100|p:10' now is ['A:100','p:10']
    vardict={}
    for c in split1:
        curvar=second.split(c) # 'A:100' is now ['A','100']
        vardict[curvar[0]]=float(curvar[1])
    return vardict


def createOptDict(staticlst,vardict):
    '''
    Compare staticlst ()
    to vardict (which is a dictionary of all variables and it\'s
    value) and make a dict of variables to optimize as keys
    and their initial value as values.

    Parameters
    ----------
    staticlst : list of strings
            list of variables NOT to optimize
    vardict : dictionary
            variable namespace

    Returns
    -------
    opt_dict : dictionary
           variable namespace containing variable that are
           to be optimized.
    '''
    opt_dict = dict(zip(vardict.keys(),vardict.values()))
    if staticlst != ['']:
        for csv in staticlst:
            opt_dict.__delitem__(csv)
    return opt_dict


data_reader_map = {'step':systemid.data.time_data_file,'swept':}

class Model_Data_Handler(object):
    def __init__(self,data_type,filename,usecols,varstr,staticstr,numstr,denstr,f=None,**file_reader_kwargs):
        self.data_type = data_type
        self.filename = filename
        self.varstr = varstr
        self.numstr = numstr
        self.denstr = denstr
        self.staticstr = staticstr
        self.f = f
        vardict = VariableStrHasher(varstr)
        opt_dict = createOptDict(staticstr,vardict)
        num,self.num_dict = PolyHasher(numstr,vardict)
        den,self.den_dict = PolyHasher(denstr,vardict)
        self.data_reader = data_reader_map[data_type]
        self.data = self.data_reader(filename)
        self.data.read(usecols,**file_reader_kwargs)
        self.model = systemid.Model(self.num_dict,self.den_dict,vardict,opt_dict)

    def initOptModel(self,opt_dict):
        self.opt_model = systemid.Model(self.num_dict,self.den_dict,opt_dict)
        self.optimized_dict = opt_dict
        
    def resample(self,N):
        self.data.resample(N)

    def scale(self,whattoscale,factor):
        if whattoscale == 'all':
            self.data.scale_t(factor)
            self.data.scale_input(factor)
            self.data.scale_output(factor)
        
        elif whattoscale == 't':
            self.data.scale_t(factor)
            
        elif whattoscale == 'input':
            self.data.scale_input(factor)
            
        elif whattoscale == 'output':
            self.data.scale_output(factor)
