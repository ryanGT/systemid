from numpy import argmax,loadtxt,arctan2,pi,arange,zeros, squeeze
from numpy import conjugate,array,log10,imag,real
from numpy.fft import fft 
import plotting
import pdb
from utils import make_same_len_if_close, to_array

def t_to_f(t):
    '''
    Calculate the frequency array that corresponds to the
    output array of `numpy.fft.fft`.

    Parameters
    ----------
    t : array
        time array

    Returns
    -------
    f : array
        frequency array
    '''
    dt = t[2]-t[1]
    T = t.max()+dt
    dt = t[2]-t[1]
    T = t.max()-t.min()+dt
    fs = 1.0/dt
    df = 1.0/T
    f = arange(0,fs,df)
    return f

def f_to_t(f,tstart=0):
    '''
    Calculate the time array that corresponds to the
    input array of `numpy.fft.fft`.

    Parameters
    ----------
    f : array
        frequency array

    Returns
    -------
    t : array
        time array
    '''
    df = f[2]-f[1]
    fs = f.max()-f.min()+dt
    T = 1.0/df
    dt = 1.0/fs
    t = arange(tstart,T,dt)
    return t

def do_fft(data,t,fixed_sine_freq=False):
    '''
    Compute the one-dimensional discrete Fourier Transform using
    `numpy.fft.fft`

    Parameters
    ----------
    data : array_like
           Data to perform fast fourier transform on.
    t : array_like
        Time array corresponding to `data`.
    fixed_sine_freq : float or int, optional
                      If `output` is known to be at a given fixed sine
                      frequency, the value of the fft at the fixed sine
                      might be the only point of interest and it will be
                      the only one returned if `fixed_sine_freq` is not None.

    Returns
    -------
    frequency_data : frequency_data instance
    '''
    U = fft(data)
    if not fixed_sine_freq:
        f = t_to_f(t)
        G = U
    else:
        f = fixed_sine_freq
        NFFT = len(U)
        u = argmax(abs(U[0:NFFT/2]))
        G = U[u]
    return frequency_data(f,G)


def read_data_file(filename,usecols,**kwargs):
    '''Return data columns from a data file read in with scipy.loadtxt().'''
    how_to_load = {'usecols':usecols,
                   'skiprows':1,
                   'unpack':True}
    how_to_load.update(kwargs)
    return loadtxt(filename,**how_to_load)

def t_data(t):
    '''
    Convenience function for time arrays.

    Parameters
    ----------
    t : array_like

    Returns
    -------
    dt : float
         time step
    T : float
        maximum time
    '''
    dt = t[2]-t[1]
    T = t.max()+dt
    return dt,T

def coherence(list_of_xs, list_of_ys,t):
    '''
    Need doc string.
    '''
    Gxx = autospectral_density(list_of_xs,t)
    Gyy = autospectral_density(list_of_ys,t)
    Gxy = crossspectral_density(list_of_xs,list_of_ys,t)
    coh = asarray([abs(cGxy)**2/cGxx/cGyy for cGxy,cGxx,cGyy in zip(Gxy,Gxx,Gyy)])
    return coh

def autospectral_density(list_of_arrays,t):
    '''
    Need doc string.
    '''
    dt,T = t_data(t)
    nd = len(list_of_arrays)
    sum = zeros(nd)
    for cur_data in zip(*list_of_arrays):
        Xk = do_fft(cur_data,t)
        sum+=abs(Xk.spectrum)**2
    Gxx = 2.0/nd/T*sum
    return asarray(Gxx)

def crossspectral_density(list_of_xs,list_of_ys,t):
    '''
    Need doc string.2
    '''
    dt,T = t_data(t)
    nd = len(list_of_xs[:,1])
    sum = zeros(nd)
    for i in range(len(zip(*list_of_xs))):
        Xk = do_fft(list_of_xs[:,i],t)
        Yk = do_fft(list_of_ys[:,i],t)
        Xkconj = conjugate(Xk.spectrum)
        sum = [s+cX*cY for s,cX,cY in zip(sum,Xkconj,Yk.spectrum)]
    Gxy = 2.0/nd/T*asarray(sum)
    return Gxy

def clean_encoder_signals(A,B,square_wave_mag = 5.0):
    '''
    Need doc string.
    '''
    Max = square_wave_mag
    A[A<.5*Max] = 0.0
    A[A>=.5*Max] = 1.0
    B[B<.5*Max] = 0.0
    B[B>=.5*Max] = 1.0
    return A,B

def decode_encoder(A,B):
    '''
    Need doc string.
    '''
    i = 1
    counts = zeros(len(A))
    counts = counts.tolist()
    step = 0
    steptot = 0
    itterations = 1
	
    for i in range(1,len(A)):
        if A[i] != A[i-1]:
            if A[i] != B[i]:
                step += 1.0
            elif A[i] == B[i]:
                step += -1.0
        elif B[i] != B[i-1]:
            if B[i] == A[i]:
                step += 1.0
            if B[i] != A[i]:
                step += -1.0
            else:
                step = 0
        steptot += step
        counts[i] = steptot
        itterations += 1
    return array(counts)

class data_base_class(object):
    '''
    Need doc string.
    '''
    def resample(self,n):
        inds = arange(0,len(self.t),n)
        self.input = self.input[inds]
        self.t = self.t[inds]
        self.output = self.output[inds]

class time_data(data_base_class):
    def __init__(self,t,input,output):
        '''
        Need doc string.
        '''
        self.t = to_array(t)
        self.input = to_array(input)
        self.output = to_array(output)
        self.raw_t = to_array(t)
        self.raw_input = to_array(input)
        self.raw_output = to_array(output)
        self.dt = self.t[2]-self.t[1]
        self.T = self.t.max()+self.dt

    def scale_t(self,value):
        '''
        Need doc string.
        '''
        self.t = self.t*value

    def scale_input(self,value):
        '''
        Need doc string.
        '''
        self.input = self.input*value

    def scale_output(self,value):
        '''
        Need doc string.
        '''
        self.output = self.output*value

    def remove_mean(self):
        '''
        Need doc string.
        '''
        self.output = self.output-self.output.mean()

    def input_spectrum(self,fixed_sine_freq=False):
        '''
        Need doc string.
        '''
        return do_fft(self.input,self.t,fixed_sine_freq)

    def ouput_spectrum(self,fixed_sine_freq=False):
        '''
        Need doc string.
        '''
        return do_fft(self.input,self.t,fixed_sine_freq)
 
    def experimental_transferfunction(self,fixed_sine_freq=False,trim_at_nyquist=False):
        '''
        Need doc string.
        '''
        U = fft(self.input)
        Y = fft(self.output)
        if not fixed_sine_freq:
            f = t_to_f(self.t)
            exp_tf = Y/U
            if trim_at_nyquist:
                f = f[0:len(f)/2]
                exp_tf = exp_tf[0:len(exp_tf)/2]
        else:
            f = fixed_sine_freq
            NFFT = len(U)
            u = argmax(abs(U[0:NFFT/2]))
            exp_tf = Y[u]/U[u]
        return frequency_data(f,exp_tf)
        
    def plot_raw_input(self,**plot_options):
        '''
        Need doc string.
        '''
        return plotting.plot_time(self.raw_t,self.raw_input,**plot_options)        

    def plot_raw_output(self,**plot_options):
        '''
        Need doc string.
        '''
        return plotting.plot_time(self.raw_t,self.raw_output,**plot_options)        

    def plot_raw(self,**plot_options):
        '''
        Need doc string.
        '''
        self.plot_raw_input(**plot_options)
        plot_options['clear']=False
        self.plot_raw_output(**plot_options)

    def plot_input(self,**plot_options):
        '''
        Need doc string.
        '''
        return plotting.plot_time(self.t,self.input,**plot_options)

    def plot_output(self,**plot_options):
        '''
        Need doc string.
        '''
        return plotting.plot_time(self.t, self.output,**plot_options)


class encoder_time_data(time_data):
    def __init__(self,t,input,A,B):
        '''
        Need doc string.
        '''
        self.t = self.encoder_t = to_array(t)
        self.input = to_array(input)
        self.A = to_array(A)
        self.B = to_array(B)

    def clean(self,square_wave_mag=5.0):
        '''
        Need doc string.
        '''
        self.A,self.B = clean_encoder_signals(self.A,self.B,\
                                                  square_wave_mag = square_wave_mag)

    def decode(self):
        '''
        Need doc string.
        '''
        self.output = decode_encoder(self.A,self.B)
        time_data.__init__(self,self.t,self.input,self.output)

    def plot_A(self,**plot_options):
        plotting.plot_time(self.encoder_t,self.A,**plot_options)

    def plot_B(self,**plot_options):
        plotting.plot_time(self.encoder_t,self.B,**plot_options)

    def plot_AB(self,**plot_options):
        self.plot_A(**plot_options)
        plot_options['clear']=False
        self.plot_B(**plot_options)
        
class frequency_data(data_base_class):
    def __init__(self,f,spectrum):
        '''
        Need doc string.
        '''
        self.f = to_array(f)
        self.spectrum = to_array(spectrum)
        self.M_in_db()
        self.phase_in_deg()

    def trim_at_freq(self,f):
        ind = self.f<f
        self.spectrum = self.spectrum[ind]
        self.f = self.f[ind]
        
    def calc_magnitude(self):
        '''
        Need doc string.
        '''
        self.M = abs(self.spectrum)
        
    def calc_phase(self):
        '''
        Need doc string.
        '''
        self.phase_in_rad = arctan2(imag(self.spectrum),real(self.spectrum))

    def M_in_db(self):
        '''
        Need doc string.
        '''
        if not hasattr(self,'M'):
            self.calc_magnitude()
        self.dbM = 20*log10(self.M)
        
    def phase_in_deg(self):
        '''
        Need doc string.
        '''
        if not hasattr(self,'phi'):
            self.calc_phase()
        self.phase_in_deg = self.phase_in_rad*180.0/pi
        self.phase = self.phase_in_deg

    def plot_bode(self,**plot_options):
        '''
        Need doc string.
        '''
        f = self.f
        dbM,phase = make_same_len_if_close(self.dbM,self.phase)
        return plotting.plot_bode(dbM,phase,f,**plot_options)

class frequency_data_in_db_w_phase(frequency_data):
    def __init__(self,f,dbM):
        self.f = asarray(f)
        self.dbM = asarray(dbM)

    def calc_magnitude(self):
        pass

    def calc_phase(self):
        pass

    def M_in_db(self):
        pass

    def phase_in_deg(self):
        pass

class time_data_file(time_data):
    def __init__(self,filename):
        '''
        Need doc string.
        '''
        self.filename = filename
        
    def read(self,usecols,**kwargs):
        '''
        Need doc string.
        '''
        self.t,self.input,self.output = read_data_file(self.filename,usecols,**kwargs)
        time_data.__init__(self,self.t,self.input,self.output)


class frequency_data_file(frequency_data):
    def __init__(self,filename):
        self.filename = filename

    def read(self,usecols,**kwargs):
        self.f,self.spectrum = read_data_file(self.filename,usecols,**kwargs)
        frequency_data.__init__(self,self.f,self.spectrum)

class frequency_data_from_rwkbode(frequency_data):
    """Class to form bridge between the system ID module and the
    rwkbode data class of Ryan Krauss."""
    def __init__(self, f, rwkbode_instance):
        """Initialize a frequency_data_from_rwkbode instance based on
        a frequency vector and an rwkbode_instance."""
        self.f = f
        self.M = squeeze(rwkbode_instance.mag)
        self.phase = squeeze(rwkbode_instance.phase)
        self.dbM = squeeze(rwkbode_instance.dBmag())

class frequency_data_file_in_db_w_phase(frequency_data_in_db_w_phase):
    def __init__(self,filename):
        self.filename = filename

    def read(self,usecols,**kwargs):
        self.f,self.dbM,self.phase = read_data_file(self.filename,usecols,**kwargs)
        frequency_data.__init__(self,self.f,self.dbM)
    
class encoder_time_data_file(time_data_file,encoder_time_data):
    def read(self,usecols,decode=True,clean=True,square_wave_mag=5.0,**kwargs):
        '''
        Need doc string.
        '''
        t,input,A,B = read_data_file(self.filename,usecols,**kwargs)
        encoder_time_data.__init__(self,t,input,A,B)
        if decode:
            self.clean(square_wave_mag)
            self.decode()
        


class multiple_data(time_data):
    def __init__(self,t,inputmat,outputmat):
        '''
        Need doc string.
        '''
        self.inputmat = inputmat
        self.outputmat = outputmat
        self.t = t
        self.average()

    def average(self):
        '''
        Need doc string.
        '''
        self.input = self.inputmat.mean(axis=1)
        self.output = self.outputmat.mean(axis=1)

    def calc_coherence(self):
        '''
        Need doc string.
        '''
        self.coherence = coherence(self.inputmat,self.outputmat,self.t)

    def plot_coherence(self,**plot_options):
        f = t_to_f(self.t)
        if not hasattr(self,'coherence'):
            self.calc_coherence
        return plotting.plot_coherence(self.coherence,f,**plot_options)

class multiple_data_files(multiple_data):
    def __init__(self,file_name_list):
        '''
        Need doc string.
        '''
        self.filenames = file_name_list

    def read_and_average(self,usecols,**kwargs):
        '''
        Need doc string.
        '''
        i=0
        for j,curfile in enumerate(self.filenames):
            ct,cin,cout = read_data_file(curfile,usecols,**kwargs)
            if i == 0:
                inmat = outmat = zeros((ct.shape[0], len(self.filenames)))
            inmat[:,j] = cin
            outmat[:,j] = cout
            i+=1
        self.t = ct
        multiple_data.__init__(self,self.t,inmat,outmat)
        self.average()

    def read(self,usecols,**kwargs):
        '''
        Need doc string.
        '''
        self.read_and_average(usecols,**kwargs)

class multiple_data_encoder_files(multiple_data_files):
    def read_and_average(self,tcol,incol,Acol,Bcol,**kwargs):
        '''
        Need doc string.
        '''
        Amat = Bmat = zeros((th.shape[0], len(self.filenames)))
        usecols = (tcol,incol, Acol,Bcol)
        for j,curfile in enumerate(self.filenames):
            ct,cin,cA,cB = read_data_file(curfile,usecols,**kwargs)
            Amat[:,j] = cA
            Bmat[:,j] = cB
        self.t = ct
        self.input = cin
        self.A = Amat.mean(axis=1)
        self.B = Bmat.mean(axis=1)

