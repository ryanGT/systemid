from pylab import figure,show,legend

standard_kwargs = {'fig':None,'legend':None,'clear':True,
                   'fignum':1,'legendpos':4,'linestyle':'-','markersize':12,
                   'linewidth':1,'marker':''}

               
def _combine_dicts(primary,secondary):
    '''
    Combine `primary` and `secondary` by overriding or adding
    all of `primary`s keys and their corresponding values
    to `secondary`.  This function is to similar to updating a dictionary
    but it will also add the new items if necessary.

    Parameters
    ----------
    primary : dictionary
              The dictionary items that are to update or be added to
              secondary.
    secondary : dictionary
              The dictionary that needs updated and added to.
    Returns
    -------
    new_dict : dictionary
              The new dictionary containing all the items in `primary`
              and also the items in `secondary` that were not in `primary`
    '''
    new_dict = secondary
    for k,v in primary.items():
        new_dict[k]=v
    return secondary

def plot_time(t,y,**kwargs):
    '''
    Plot `y` vs `t` and label the figure as such.

    Parameters
    ----------
    t : array
    y : array

    Returns
    -------
    fig : instance of `matplotlib.figure.Figure`
    '''

    options = {'title':'Time Domain','xlabel':'Time (s)',
        'ylabel':'y(t)','label':None}
    options = _combine_dicts(options,standard_kwargs)
    options.update(kwargs)
    if not options['fig']:
        fig = figure(options['fignum'])
    else:
        fig = options['fig']
    if options['clear']:
        fig.clear()
    ax = fig.add_subplot(111)
    if not hasattr(y[0],'__len__'):
        y = [y]
    for cy in y:
        ax.plot(t,cy,linestyle=options['linestyle'],label=options['label'],linewidth=options['linewidth'])
    if options['label']:
        ax.legend(loc=0)
        #ax.legend(options['legend'],options['legendpos'])
    ax.set_title(options['title'])
    ax.set_xlabel(options['xlabel'])
    ax.set_ylabel(options['ylabel'])
    return fig

def plot_bode(M,phi,f,**kwargs):
    '''
    Plot the Bode Plot of the magnitude `M` and phase `phi`
    with the frequency `f`.

    Parameters
    ----------
    M : array
    phi : array
    f : array
    kwargs :
    
    Returns
    -------
    fig : instance of `matplotlib.figure.Figure`
    '''
    options = {'title':'Bode Plot', 'xlabel':'Freq. (Hz)',
               'maglabel':'Mag. Ratio (dB)','label':None,\
               'phaselabel':'Phase (deg.)','linestyle':'-'}
    options = _combine_dicts(options,standard_kwargs)
    options.update(kwargs)
    if hasattr(M,'__len__'):
        if not hasattr(M[0],'__len__'):
            M = [M]
            phi = [phi]
    else:
        M = [[M]]
        phi = [[phi]]
    if not hasattr(f,'__len__'):
        f = [f]
    if not options['fig']:
        fig = figure(options['fignum'])
    else:
        fig = options['fig']
    if options['clear']:
        fig.clf()
    ax1 = fig.add_subplot(211)
    _plot_bode_lines(ax1,f,M,**options)
    ax1.set_ylabel(options['maglabel'])
    ax2 = fig.add_subplot(212)
    _plot_bode_lines(ax2,f,phi,**options)
    ax2.set_ylabel(options['phaselabel'])
    if options['label']:
        ax1.legend()#a1.options['legend'],options['legendpos'])
    for ax in fig.axes:
        ax.grid(True)
    return fig

def plot_coherence(coh,f,**kwargs):
    '''
    Plot the coherence against the frequency f.

    Parameters
    ----------
    coh : array
    f : array
    kwargs :
    
    Returns
    -------
    fig : instance of `matplotlib.figure.Figure`
    '''
    options = {'title':'Coherence', 'xlabel':'Freq. (Hz)',
               'ylabel':'$\gamma^2_{xy}(f)$','label':None,\
               'phaselabel':'Phase (deg.)','linestyle':'-'}
    options = _combine_dicts(options,standard_kwargs)
    options.update(kwargs)
    if abs(len(f)-len(coh))==1:
        if len(coh)>len(f):
            coh = coh[:-1]
        else:
            f = f[:-1]
    if hasattr(coh,'__len__'):
        if not hasattr(coh[0],'__len__'):
            coh = [coh]
    else:
        coh = [[coh]]
    if not hasattr(f,'__len__'):
        f = [f]
    if not options['fig']:
        fig = figure(options['fignum'])
    else:
        fig = options['fig']
    if options['clear']:
        fig.clf()
    ax1 = fig.add_subplot(111)
    _plot_bode_lines(ax1,f,coh,**options)
    ax1.set_ylabel(options['ylabel'])
    if options['label']:
        ax1.legend()#a1.options['legend'],options['legendpos'])
    for ax in fig.axes:
        ax.grid(True)
    return fig

def _plot_bode_lines(ax,x,y,**options):
    '''
    Plot `y` vs `x` on `ax`.

    Parameters
    ----------
    ax : instance of `matplotlib.axis.Axis`
    x : array
    y : array

    Returns
    -------
    None
    '''
    for cy in y:
        #if len(cy)==1:
        #    linestyle='o'
        #else:
        #    linestyle='-'
        ax.semilogx(x,cy,linestyle=options['linestyle'],marker=options['marker'],label=options['label'])

