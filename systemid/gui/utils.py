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

def PolyHasher(instr,vardict,myvar='s'):
    '''Parse a string such as s^2+2s+2 and turn it
    into a list of coefficients and a dictionary
    with keys corresponding to the power of myvar and
    values corresponding to the coefficients.instr. Will most likely
    come from something like a wx.TextCtrl.

    Parameters
    ----------
    instr : string
        polynomial representation ('s^2+p*s+1')

    Returns
    -------
    polylist : list
           List suitable for poly1d
    coeff_dict : dictionary
           Dictionary representation of the polynomial
    '''
    polynomial = str2sympypoly(instr,myvar,vardict)
    coeff_dict = polynomial_as_dict(polynomial)
    coeff_dict = _fill_coeff_dict(coeff_dict,polynomial.degree)
    polylst = systemid.utils.exec_coeffs(coeff_dict,vardict)
    return polylst,coeff_dict


def str2sympypoly(instr,myvar,vardict):
    '''Convert instr (i.e. s*(s+p)) to a sympy Poly instance and expand it.
    Inputs:  instr - string representation of a polynomial.
    Outputs: outpoly - sympy Poly instance representing instr'''
    expr = sympy.sympify(instr)
    expanded_expr = expr.expand()
    outpoly = expanded_expr.as_poly(myvar)
    return outpoly
    
def _fill_coeff_dict(coeff_dict,polydegree):
    '''
    Fill a polynomial coeff_dict to have values for all degrees up to
    poly degree. i.e. s^2+1 will not have a representation of 0 for s
    until coeff_dict is put through this function.

    Parameters
    ----------
    coeff_dict : dictionary
    polydegree : integer

    Returns
    -------
    coeff_dict : dictionary
    '''
    polydegree=int(polydegree)
    for c in range(polydegree+1):
        str_c = str(c)
        if not coeff_dict.has_key(str_c):
            coeff_dict[str_c]='0'
    return coeff_dict

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

def polynomial_as_dict(polynomial):
    '''Convert polynomial into dict.

    Parameters
    ----------
    polynomial : sympy.Add instance

    Returns
    -------
    poly_dict  d :  polynomial as dict mapped to a string
    '''
    return  dict(map(lambda x:(str(x[0][0]),str(x[1])),polynomial.as_dict().items()))


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
