import sympy
from numpy import asarray

def to_array(a):
    if not hasattr(a,'__len__'):
        a = [a]
    return asarray(a)

def make_same_len_if_close(a,b):
    '''
    If len(a)-len(b) == 1 then they are close enough, trim
    accordingly.
    '''
    if abs(len(a)-len(b)) == 1:
        if len(b)<len(a):
            a = a[:len(b)]
        else:
            b = b[:len(a)]
    elif abs(len(a)-len(b)) > 1:
        print 'a and b are different lenghts'
    return a,b

def var_dict_w_new_values(new_values,model):
    new_var_dict = dict(zip(model.opt_dict.keys(),new_values)) 
    for ck,cv in model.var_dict.iteritems():
        if not new_var_dict.has_key(ck):
            new_var_dict[ck]=cv
    return new_var_dict

def OptNumDen(new_values,model):
    '''
    Make two lists `num` and `den` suitable for `poly1d()` and a
    new variable dictionary by comparing the values that are
    allowed to be optimized `opt_values`
    and `opt_lst` to the original variables in `var_dict`.  

    Parameters
    ----------
    opt_values : list of floats or integers
                 is a list of optimized variable values and
    opt_lst : list of strings
              Symbolic representations of the values in `opt_values`.
    var_dict : dictionary
               Variable namespace.
    num_dict : 
    den_dict : and den_dict are the numerator

    Returns
    -------
    num : list
          Represents a numerator polynomial. (see `poly1d`)
    den : list
          Represents a denomenator polynomial.
    new_var_dict : dicionary
          Variable namespace.

    Todo
    ----
    Look into using a dictionary as a parameter called `opt_dict`
    in place of the two lists `opt_values` and `opt_lst`.
    '''
    new_var_dict = var_dict_w_new_values(new_values,model)
    num = _exec_coeffs(model.num_dict,new_var_dict)
    den = _exec_coeffs(model.den_dict,new_var_dict)
    return num,den,new_var_dict

def _exec_coeffs(coeff_dict,vardict):
    '''
    See `exec_coeffs`.
    '''
    polylst=[]
    for k in sorted(coeff_dict.keys(),reverse=True):
        cp = eval(coeff_dict[k],vardict)
        polylst.append(cp)
    if vardict.has_key('__builtins__'):
        vardict.__delitem__('__builtins__')
    return polylst

def exec_coeffs(coeff_dict,var_dict):
    '''
    Execute all the coefficient string expresions and return a list
    suitable for `poly1d`.

    Parameters
    ----------
    coeff_dict : dictionary
    vardict : dictionary
              Variable namespace.

    Returns
    -------
    polylst : list
              Represents a polynomial. see `poly1d`
    '''
    return _exec_coeffs(coeff_dict,var_dict)

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
    polylst = exec_coeffs(coeff_dict,vardict)
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

def poly_var_map(power_str,myvar):
    if power_str == '1':
        return '*'+myvar
    elif power_str == '0':
        return ''
    else:
        return '*'+myvar+'**'+power_str

def poly_dict_to_str(in_dict, myvar='s'):
    keys = in_dict.keys()
    keys.sort(reverse=True)
    poly_str = in_dict[keys[0]]+poly_var_map(keys[0],myvar)
    if len(keys)>1:
        for key in keys[1:]:
            poly_str+=in_dict[key]
            poly_str+=poly_var_map(key,myvar)
    return poly_str
