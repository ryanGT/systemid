from numpy import arange, sin, pi
import matplotlib,wx
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

class CanvasPanel(wx.Panel):
    def __init__(self,parent,figsize=(6,6)):
        wx.Panel.__init__(self,parent)
        self.SharedVariables()
        self.figure = Figure(figsize=figsize)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.SetColor(None)
        buttongrid = self.ButtonGrid()
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_toolbar(sizer)
        sizer.Add(self.canvas, 0)
        sizer.Add(buttongrid,0,wx.ALIGN_CENTER_HORIZONTAL)
        hbox.Add(sizer,0)
        self.SetSizer(sizer)
        self.Show(True)

    ###################
    # Shared Variables
    ###################

    def SharedVariables(self):
        '''Get variables defined by another panel, needed
           by this panel.'''
        self._definecurpanel
        
    ##############
    # Boxes/Grids
    ##############

    def ButtonGrid(self):
        grid = wx.FlexGridSizer(1,5,0,0)
        x = wx.ALIGN_CENTER_HORIZONTAL
        rawdatabutton = wx.Button(self,-1,'Raw Data')
        self.Bind(wx.EVT_BUTTON,self.OnPlotRawDataClick,rawdatabutton)
        timeplotbutton = wx.Button(self,-1,'Time Plot')
        self.Bind(wx.EVT_BUTTON,self.OnTimePlotClick,timeplotbutton)
        self.freqplotbutton = wx.Button(self,-1,'Bode Plot')
        self.Bind(wx.EVT_BUTTON,self.OnFreqPlotClick,self.freqplotbutton)
        self.optimizebutton = wx.Button(self,-1,'Optimize')
        self.Bind(wx.EVT_BUTTON,self.OnOptimizeClick,self.optimizebutton)
        clearfigbutton = wx.Button(self,-1,'Clear')
        self.Bind(wx.EVT_BUTTON, self.OnCLF, clearfigbutton)
        grid.Add(rawdatabutton,0,wx.ALIGN_CENTER_HORIZONTAL)
        grid.Add(timeplotbutton,0,wx.ALIGN_CENTER_HORIZONTAL)
        grid.Add(self.freqplotbutton,0,wx.ALIGN_CENTER_HORIZONTAL)
        grid.Add(self.optimizebutton,0,x)
        grid.Add(clearfigbutton,0)
        return grid

    def add_toolbar(self,sizer):
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        tw, th = self.toolbar.GetSizeTuple()
        fw, fh = self.canvas.GetSizeTuple()
        self.toolbar.SetSize(wx.Size(fw, th))
        sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        self.toolbar.update()

    ########
    # Misc.
    ########

    def _definecurpanel(self):
        self.curpanel = self.Parent.Parent#self.Parent.curpanel

    def RenewCurpanel(self):
        self._definecurpanel()

    def Plot(self,x,y,**kwargs):
        if type(x)==list:
            for cx, cy in zip(x,y):
                self.axes.plot(cx,cy)
        else:
            self.axes.plot(x,y)
        self.canvas.draw()

    def show(self):
        self.ReDraw()
        
    def ReDraw(self):
        self.canvas.draw()

    def clf(self):
        self.figure.clf()
        self.axes = self.figure.add_subplot(111)
        self.canvas.draw()

    def cla(self):
        self.axes.cla()
        self.canvas.draw()

    def SetColor(self, rgbtuple):
        """Set figure and canvas colours to be the same"""
        if not rgbtuple:
            rgbtuple = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE).Get()
        col = [c/255.0 for c in rgbtuple]
        self.figure.set_facecolor(col)
        self.figure.set_edgecolor(col)
        self.canvas.SetBackgroundColour(wx.Colour(*rgbtuple))

    #########################
    # Widget Bound Functions
    #########################

    def OnPlot(self,e):
        self.Plot()

    def OnCLA(self,e):
        self.cla()

    def OnCLF(self,e):
        self.clf()

    def OnPaint(self, event):
        self.canvas.draw()

    def OnFreqPlotClick(self,e):
        self.RenewCurpanel()
        self.curpanel.FreqPlot()

    def OnTimePlotClick(self,e):
        self.RenewCurpanel()
        self.curpanel.TimePlot()
        
    def OnPlotRawDataClick(self,e):
        self.RenewCurpanel()
        self.curpanel.RawDataPlot()
        
    def OnOptimizeClick(self,e):
        self.RenewCurpanel()
        self.curpanel.Optimize()



