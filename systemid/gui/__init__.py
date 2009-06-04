import wx,os,pickle
import utils,systemid
from filechooser import rwkSingleFileChooser
import wxcanvas, frames

packagedir=os.path.split(__file__)[0]
savefile = os.path.join(packagedir,'sysidgui_setting.pkl')

__all__ = ['utils','frames','wxcanvas']
    
class SIG(wx.App):
    def OnInit(self):
        frame = frames.SIGFrame(None,'System Identification Tools')
        frame.Show(True)
        return True
