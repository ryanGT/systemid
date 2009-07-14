#!/usr/bin/python

from systemid.gui import *
import systemid

if __name__ == '__main__':
    app = systemid.gui.SIG(redirect=False)
    app.MainLoop()
