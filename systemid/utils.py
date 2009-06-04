def OptNumDen(opt_values,opt_lst,var_dict,num_dict,den_dict):
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
    new_var_dict = dict(zip(opt_lst,opt_values)) 
    for ck,cv in var_dict.iteritems():
        if not new_var_dict.has_key(ck):
            new_var_dict[ck]=cv
    num = _exec_coeffs(num_dict,new_var_dict)
    den = _exec_coeffs(den_dict,new_var_dict)
    return num,den,new_var_dict

def _exec_coeffs(coeff_dict,vardict):
    '''
    See `exec_coeffs`.
    '''
    polylst=[]
    for k in sorted(coeff_dict.keys(),reverse=True):
        cp = eval(coeff_dict[k],vardict)
        polylst.append(cp)
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
