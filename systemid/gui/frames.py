import wx,os,pickle
import wxcanvas
import systemid
import utils
from filechooser import rwkSingleFileChooser
packagedir=os.path.split(__file__)[0]
savefile = os.path.join(packagedir,'sysidgui_setting.pkl')


class MyStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)
        self.SetFieldsCount(2)
        self.SetStatusText('Welcome to Sytem ID GUI!', 0)
        self.SetStatusWidths([0, 0])

class PreviewDialog(wx.Dialog):
    def __init__(self, parent, id, title,filename):
        wx.Dialog.__init__(self, parent, id, title, size=(500, 500))
        self.panel = wx.Panel(self,-1,size=(200,200))
        self.panel.SetBackgroundColour('white')
        grid = wx.FlexGridSizer(1,15,5)
        display = self.createDisplay(filename)
        grid.Add(display,wx.EXPAND)
        self.panel.SetSizer(grid)
        self.panel.Fit()
        self.Fit()

    def createDisplay(self,filename):
        f = open(filename,'r')
        text = f.read()
        f.close()
        display = wx.TextCtrl(self, -1, value=text,\
                                    size=(450, 450),\
                                    style=wx.TE_MULTILINE|\
                                    wx.HSCROLL|wx.TE_READONLY)
        #display.SetScrollbars(0, 17, 0, 55)
        return display

class LoadDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(400, 200))
        self.panel = wx.Panel(self,-1)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.chooserpanel = rwkSingleFileChooser(self.panel,-1)
        #self.chooserpanel.SetPath('')
        vbox.Add(self.chooserpanel,1,wx.EXPAND)
        
        grid = wx.FlexGridSizer(1,2,2,2)
        self.filetypebox = self.FileTypeBox()
        grid.Add(self.filetypebox,0)

        self.settingsbox = self.InputBox()
        grid.Add(self.settingsbox,0)
        
        vbox.Add(grid,0)
        
        buttons = self._makeButtons()
        vbox.Add(buttons)

        self.panel.SetSizer(vbox)
        self.SetInitialValues()
        self.panel.Layout()
        self.panel.Fit()
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.panel)
        self.SetSizer(mainsizer)
        self.Layout()
        self.Fit()

    def SetInitialValues(self):
        if self.Parent.loaddict:
            loaddict = self.Parent.loaddict
            self.tcol.SetValue(str(loaddict['tcol']))
            self.incol.SetValue(str(loaddict['incol']))
            self.outcol.SetValue(str(loaddict['outcol']))
            self.skiprows.SetValue(str(loaddict['skiprows']))
            self.chooserpanel.SetPath(loaddict['thefile'])
            self.type = loaddict['type']
            ff = loaddict['fixedfreq'] 
            if ff:
                self.fixedfreq.SetValue(str(ff))
            if self.type == 'step':
                self.stepcheck.SetValue(True)
                self.OnStepCheck(-1)
            elif self.type == 'fixed':
                self.fixedcheck.SetValue(True)
                self.OnFixedCheck(-1)
            elif self.type == 'swept':
                self.sweptcheck.SetValue(True)
                self.OnSweptCheck(-1)
        else:
            self.tcol.SetValue('0')
            self.incol.SetValue('1')
            self.outcol.SetValue('2')
            self.skiprows.SetValue('1')
            self.stepcheck.SetValue(True)
            self.type = 'step'
            self.fixedfreq.Disable()

    def _makeButtons(self):
        grid = wx.FlexGridSizer(1,3,1,1)
        previewbutton = wx.Button(self.panel,-1,'Preview')
        previewbutton.Bind(wx.EVT_BUTTON,self.OnPreview)
        loadbutton = wx.Button(self.panel,-1,'Load')
        loadbutton.Bind(wx.EVT_BUTTON,self.OnLoad)
        closebutton = wx.Button(self.panel,-1,'Close')
        closebutton.Bind(wx.EVT_BUTTON,self.OnClose)
        grid.Add(previewbutton)
        grid.Add(loadbutton)
        grid.Add(closebutton)
        return grid

    def FileTypeBox(self):
        stbox = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Data Type'), orient=wx.VERTICAL)
        grid = wx.FlexGridSizer(4,2,0,0)
        self.stepcheck = wx.CheckBox( self.panel, -1, 'Step Input' )
        self.fixedcheck = wx.CheckBox( self.panel, -1, 'Fixed Sine Input' )
        self.sweptcheck = wx.CheckBox( self.panel, -1, 'Swept Sine Input' )
        stfixedfreq = wx.StaticText(self.panel,-1,'Input Frequency: ')
        self.fixedfreq = wx.TextCtrl(self.panel,-1,size=(50,-1))
        wx.EVT_CHECKBOX(self, self.stepcheck.GetId(),\
                        self.OnStepCheck)
        wx.EVT_CHECKBOX(self, self.fixedcheck.GetId(),\
                        self.OnFixedCheck)
        wx.EVT_CHECKBOX(self, self.sweptcheck.GetId(),\
                        self.OnSweptCheck)
        x = wx.ALIGN_CENTER_VERTICAL
        grid.AddMany([(self.stepcheck,0,x),\
                      ((1,1),0),(self.fixedcheck,0,x),\
                      ((1,1),0),\
                      (stfixedfreq,0,x),\
                      (self.fixedfreq,0,x),\
                      (self.sweptcheck,0,x)])
        stbox.Add(grid,0)
        return stbox

    def InputBox(self):
        stbox = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Inputs'), orient=wx.VERTICAL)
        grid = wx.FlexGridSizer(4,2,0,0)
        stt = wx.StaticText(self.panel,-1,'Time Column: ')
        stIN = wx.StaticText(self.panel,-1,'Input Column: ')
        stOUT = wx.StaticText(self.panel,-1,'Output Column: ')
        self.incol = wx.TextCtrl(self.panel,-1,size=(50,-1))
        self.outcol = wx.TextCtrl(self.panel,-1,size=(50,-1))
        self.tcol = wx.TextCtrl(self.panel,-1,size=(50,-1))
        stskip = wx.StaticText(self.panel,-1,'Skip Rows')
        self.skiprows = wx.TextCtrl( self.panel, -1, size=(30,-1))
        stb3 = wx.StaticText(self.panel,-1,'') 
        grid.AddMany([(stt,0,wx.ALIGN_CENTER_VERTICAL),\
                      (self.tcol,0,wx.ALIGN_CENTER_VERTICAL),\
                      (stIN,0,wx.ALIGN_CENTER_VERTICAL),\
                      (self.incol,0,wx.ALIGN_CENTER_VERTICAL),\
                      (stOUT,0,wx.ALIGN_CENTER_VERTICAL),\
                      (self.outcol,0,wx.ALIGN_CENTER_VERTICAL),\
                      (stskip,0,wx.ALIGN_CENTER_VERTICAL),\
                      (self.skiprows,0,wx.ALIGN_CENTER_VERTICAL)])
        stbox.Add(grid,0)
        return stbox

    def OnStepCheck( self, evt):
        self.fixedcheck.SetValue(False)
        self.sweptcheck.SetValue(False)
        self.fixedfreq.Disable()
        self.type='step'

    def OnFixedCheck(self,evt):
        self.stepcheck.SetValue(False)
        self.sweptcheck.SetValue(False)
        self.fixedfreq.Enable()
        self.type='fixed'

    def OnSweptCheck(self,evt):
        self.stepcheck.SetValue(False)
        self.fixedcheck.SetValue(False)
        self.fixedfreq.Disable()
        self.type='swept'

    def OnPreview(self,evt):
        #f = open(self.chooserpanel.GetPath(),'r')
        #text = f.read()
        #f.close()
        #previewdialog = wx.wxScrolledMessageDialog ( self, text, 'Preview Data File' )
        
        previewdia = PreviewDialog(self, -1, 'Preview File',self.chooserpanel.GetPath())
        previewdia.ShowModal()
        previewdia.Destroy()

    def OnLoad(self,evt):
        filename = self.chooserpanel.GetPath()
        self.Parent.type = self.type
        self.Parent.filename=filename
        self.Parent.tcol = int(self.tcol.GetValue())
        self.Parent.incol = int(self.incol.GetValue())
        self.Parent.outcol = int(self.outcol.GetValue())
        self.Parent.skiprows = int(self.skiprows.GetValue())
        if self.type=='fixed':
            self.Parent.fixedfreq=float(self.fixedfreq.GetValue())
        else:
            self.Parent.fixedfreq=False
        #self.Parent.OnInitializeClick(-1)
        if self.type=='step':
            self.Parent.disable_bode=True
        else:
            self.Parent.disable_bode=False
        self.Parent.maindict,self.Parent.loaddict = self.Parent._getSaveDicts()
        self.OnClose(-1)

    def OnClose(self,evt):
#        self.SaveSettings()
        self.Destroy()

class SIGFrame(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,-1,title,size=(1200,725))
        #self.statusbar = MyStatusBar(self)
        self.LoadSettings()
        menuBar = wx.MenuBar()
        file_menu = wx.Menu()
        quit = wx.MenuItem(file_menu,1, '&Quit\tCtrl+Q')
        load = wx.MenuItem(file_menu,2,'&Load\tCtrl+L')
        file_menu.AppendItem(quit)
        file_menu.AppendItem(load)
        self.Bind(wx.EVT_MENU, self.OnClose, id=1)
        self.Bind(wx.EVT_MENU, self.OnLoad, id=2)
        menuBar.Append(file_menu, '&File')
        self.SetMenuBar(menuBar)

		
        self.panel = wx.Panel(self,-1)
        self.panel.curpanel = None
        self.panel.system = None
        self.plotpanel = wxcanvas.CanvasPanel(self.panel)
        self.plotpanel.system = None
        self.panel.plotpanel = self.plotpanel
        self.topsizer = wx.FlexGridSizer(1,2,0,0)
        leftsizer = self.LeftSizer()
        self.topsizer.Add(leftsizer,0,wx.ALL|wx.RIGHT,5)
        self.topsizer.Add(self.plotpanel,0,wx.ALL,0)
        
        self.panel.SetSizer(self.topsizer)
        self.SetInitialValues()
        self.panel.Layout()
        self.panel.Fit()
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(self.panel)
        #mainsizer.Add(self.statusbar,0)
        self.SetSizer(mainsizer)
        self.Layout()
        self.Fit()

    #####################
    # Boxes/Grids/Panels
    #####################

    def LeftSizer(self):
        topsizer = wx.FlexGridSizer(2,1,2,2)
        mainsizer = wx.FlexGridSizer(2,2,2,2)
        tfbox = self.TFBox()
        variablebox = self.VariableInputBox()
        #filetypebox = self.FileTypeBox()
        dataresizegrid = self.DataResizeGrid()

        mainsizer.Add(tfbox,0,wx.BOTTOM,2)
        mainsizer.Add(variablebox,0,wx.BOTTOM,2)
        #mainsizer.Add(filetypebox,-1)
        mainsizer.Add(dataresizegrid,-1)
        
        topsizer.Add(mainsizer,0)
        buttongrid = self.ButtonGrid()
        topsizer.Add(buttongrid,0)
  
        return topsizer

    def VariableInputBox(self):
        stbox1 = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Variables'), orient=wx.VERTICAL)
        stbox2 = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Static Variables'), orient=wx.VERTICAL)
        grid = wx.FlexGridSizer(2,1,1,1)
        self.variables = wx.TextCtrl(self.panel,-1,size=(150,-1))
        self.staticvariables = wx.TextCtrl(self.panel,-1,size=(150,-1))
        
        self.panel.variables = self.variables
        self.panel.staticvariables = self.staticvariables
        stbox1.Add(self.variables,0)
        stbox2.Add(self.staticvariables,0)
        grid.Add(stbox1,0)
        grid.Add(stbox2,0)
        return grid

    def TFBox(self):
        grid = wx.FlexGridSizer(1,1,0,0)
        stbox = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Transfer Function',size=(-1,99)), orient=wx.VERTICAL)
        grid1 = wx.FlexGridSizer(2,2,-5,0)
        stOVER = wx.StaticText(self.panel,-1,'----------------')
        stb1 = wx.StaticText(self.panel,-1,'')
        stb2 = wx.StaticText(self.panel,-1,'')
        stTF = wx.StaticText(self.panel,-1,'TF(s) = ')
        self.num = wx.TextCtrl(self.panel,-1)
        self.den = wx.TextCtrl(self.panel,-1)
        
        self.panel.num = self.num
        self.panel.den = self.den
        grid1.AddMany([(stb1,0,wx.ALIGN_CENTER_VERTICAL),(self.num,-1,wx.ALIGN_CENTER_VERTICAL),\
                       (stTF,0),(stOVER,0,wx.ALIGN_CENTER_VERTICAL),\
                      (stb2,0),(self.den,0,wx.ALIGN_CENTER_VERTICAL)])
        stbox.Add(grid1,0)
        grid.Add(stbox,0)
        return grid

    def ButtonGrid(self):
        grid = wx.FlexGridSizer(1,4,0,0)
        self.loadbutton = wx.Button(self.panel,-1,'Load',size=(55,-1))
        self.Bind(wx.EVT_BUTTON,self.OnLoad,self.loadbutton)
        self.initializebutton = wx.Button(self.panel,-1,'Init',size=(55,-1))
        self.Bind(wx.EVT_BUTTON,self.OnInitializeClick,self.initializebutton)
        self.hideplotbutton = wx.Button(self.panel,-1,'Hide Plot',size=(55,-1))
        self.Bind(wx.EVT_BUTTON, self.OnHideClick, self.hideplotbutton)
        self.closebutton = wx.Button(self.panel,-1,'Close',size=(55,-1))
        self.Bind(wx.EVT_BUTTON, self.OnClose, self.closebutton)
        grid.Add(self.loadbutton,0)
        grid.Add(self.initializebutton,0)
        grid.Add(self.hideplotbutton,0)
        grid.Add(self.closebutton,0)
        return grid

    def DataResizeGrid(self):
        stbox = wx.StaticBoxSizer(wx.StaticBox(self.panel, -1, 'Data Proc'), orient=wx.VERTICAL)
        x = wx.ALIGN_CENTER_VERTICAL
        y = wx.ALIGN_CENTER_HORIZONTAL
        grid = wx.FlexGridSizer(4,3,0,0)
        stresampleN = wx.StaticText(self.panel,-1,'Factor: ')
        self.resampleN = wx.TextCtrl(self.panel,-1,size=(50,-1))
        resamplebutton = wx.Button(self.panel,-1,'Resample',size=(55,-1))
        self.Bind(wx.EVT_BUTTON,self.OnResampleClick,resamplebutton)
        self.whattoscale = wx.ComboBox(self.panel, -1,choices=['t','IN','OUT','all'],size=(50,-1))
        stscale = wx.StaticText(self.panel,-1,'Scale')
        stby = wx.StaticText(self.panel,-1,'by')
        self.scalefactor = wx.TextCtrl(self.panel,-1,size=(50,-1))
        scaledatabutton = wx.Button(self.panel,-1,'Scale',size=(55,-1))
        self.Bind(wx.EVT_BUTTON,self.OnScaleDataClick,scaledatabutton)
        grid.Add(stresampleN,0,x)
        grid.Add(self.resampleN,0,x|y)
        grid.Add(resamplebutton,0,x|y)
        grid.Add(stscale,0,x|y)
        grid.Add(self.whattoscale,0,x|y)
        grid.Add((1,1))
        grid.Add(stby,0,x|y)
        grid.Add(self.scalefactor,0,x|y)
        grid.Add((1,1))
        grid.Add((1,1))
        grid.Add(scaledatabutton,0,x|y)
        grid.Add((1,1))
        stbox.Add(grid,0)
        return stbox


    #########################
    # Widget Bound Functions
    #########################

    def OnHideClick(self,e):
        if self.plotpanel.IsShown():
            self.plotpanel.Show(False)
            self.hideplotbutton.SetLabel('Show Plot')
        else:
            self.plotpanel.Show(True)
            self.hideplotbutton.SetLabel('Hide Plot')            
        self.panel.Fit()
        self.Fit()


    def OnInitializeClick(self,e):
        numstr = self.num.GetValue()
        denstr = self.den.GetValue()
        tcol = self.tcol
        incol = self.incol
        outcol =self.outcol
        skiprows =self.skiprows
        varstr = self.variables.GetValue()
        staticstr = self.staticvariables.GetValue()
        filename = self.filename
        data_type = self.type
        usecols = (self.tcol,self.incol,self.outcol)
        file_reader_kwargs = {'skiprows':skiprows}
        if self.type=='fixed':
            f = self.fixedfreq
            self.system = utils.Model_Data_Handler(data_type,\
                                                    filename,\
                                                    usecols,\
                                                    varstr,\
                                                    staticstr,\
                                                    numstr,\
                                                    denstr,\
                                                    f,**file_reader_kwargs)
        else:
            self.system = utils.Model_Data_Handler(data_type,\
                                                    filename,\
                                                    usecols,\
                                                    varstr,\
                                                    staticstr,\
                                                    numstr,\
                                                    denstr,**file_reader_kwargs)
                                                    

    def LoadSettings(self):
        if os.path.exists(savefile):
            f = open(savefile,'r')
            self.maindict,self.loaddict = pickle.load(f)
            f.close()
        else:
            self.maindict = False
            self.loaddict = False
        
    def _getSaveDicts(self):
        maindict = {'num':self.num.GetValue(),'den':self.den.GetValue(),\
                    'disable_bode':self.disable_bode,'whattoscale':self.whattoscale.GetValue(),\
                    'variables':self.variables.GetValue(),\
                    'staticvariables':self.staticvariables.GetValue(),\
                    'resampleN':self.resampleN.GetValue(),\
                    'scalefactor':self.scalefactor.GetValue()}

        loaddict={'tcol':self.tcol,'incol':self.incol,\
                  'outcol':self.outcol,'skiprows':self.skiprows,\
                  'type':self.type,'thefile':self.thefile,\
                  'fixedfreq':self.fixedfreq}
        return maindict,loaddict

    def SaveSettings(self):
        f = open(savefile,'wb')
        self.maindict,self.loaddict = self._getSaveDicts()
        pickle.dump((self.maindict,self.loaddict),f)
        f.close()

    def OnClose(self,event):
        self.SaveSettings()
        self.Close()


    def OnLoad(self,evt):
        loaddia = LoadDialog(self, -1, 'Load File')
        loaddia.ShowModal()
        loaddia.Destroy()
        if self.disable_bode:
            self.plotpanel.freqplotbutton.Disable()
        else:
            self.plotpanel.freqplotbutton.Enable()

    ####################
    # General Functions
    ####################

    def SetInitialValues(self):
        '''
        Set initial values for object on this panel.
        '''
        self.figure = self.plotpanel.figure
        if self.maindict:
            self.num.SetValue(self.maindict['num'])
            self.den.SetValue(self.maindict['den'])
            self.variables.SetValue(self.maindict['variables'])
            self.staticvariables.SetValue(self.maindict['staticvariables'])
            self.resampleN.SetValue(self.maindict['resampleN'])
            self.scalefactor.SetValue(self.maindict['scalefactor'])
            self.whattoscale.SetValue(self.maindict['whattoscale'])
            self.disable_bode=self.maindict['disable_bode']
            if self.maindict['disable_bode']:
                self.plotpanel.freqplotbutton.Disable()
            else:
                self.plotpanel.freqplotbutton.Enable()
            if self.loaddict:
                self.thefile = self.loaddict['thefile']
                self.tcol = int(self.loaddict['tcol'])
                self.incol =int( self.loaddict['incol'])
                self.outcol = int(self.loaddict['outcol'])
                self.skiprows = int(self.loaddict['skiprows'])
                self.type = self.loaddict['type']
                self.fixedfreq=self.loaddict['fixedfreq']
        else:
            self.disable_bode='True'
            self.type='step'
            self.thefile=''
            self.skiprows=1
            self.tcol=0
            self.incol=1
            self.outcol=2

    def RawDataPlot(self):
        '''
        Plot the raw data set.
        '''
        self.plotpanel.clf()
        self.system.data.plot_raw(**{'fig':self.figure})
        self.plotpanel.show()#ReDraw()

    def TimePlot(self):
        '''
        Plot the time respone.
        '''
        self.plotpanel.clf()
        self.system.model.plot_resp(self.system.data.t,self.system.data.input,**{'fig':self.figure})
        self.plotpanel.ReDraw()

    def FreqPlot(self):
        '''
        Plot the frequency response.
        '''
#        self.plotpanel.clf()
#        self.system.bode_plot(self.figure)
#        self.plotpanel.ReDraw()
        pass

    def Optimize(self):
        '''
        Optimize the variables. Leaving the chosen static variable constant.
        '''
        optimized_dict = systemid.fit_time(self.system.model,self.system.data)
        self.system.initOptModel(optimized_dict)
        self.system.opt_model.plot_resp(self.system.data.t,self.system.data.input,**{'fig':self.figure,'clear':True})
        self.system.data.plot_output(**{'fig':self.figure,'clear':False})
        self.plotpanel.ReDraw()

    def OnScaleDataClick(self,e):
        #self._getsystem()
        exec('factor = '+self.scalefactor.GetValue())
        whattoscale = self.whattoscale.GetValue()
        self.system.scale(whattoscale,factor)

    def OnResampleClick(self,e):
        #self._getsystem()
        N = int(self.resampleN.GetValue())
        self.system.resample(N)
        #self.system.PrintData()
