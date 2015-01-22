#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
 Name:
    Delete Padding
 Version:
    1.0 (13 December 2013)
 Author:
    Arnaud Trouve (AMFX)
 Description:  
    Rename frames in an image sequence, by removing leading zeros in the padding
    e.g. : frame_0037.jpg -> frame_37.jpg
 Usage:
    Select a directory, then "OK"
'''

import wx, os, re, sys, glob
from os import listdir
from os.path import isfile, join


# message boxes
def YesNo(parent, question, caption = 'Yes or no?'):
    dlg = wx.MessageDialog(parent, question, caption, wx.YES_NO | wx.ICON_QUESTION)
    result = dlg.ShowModal() == wx.ID_YES
    dlg.Destroy()
    return result

def Info(parent, message, caption = 'Info'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()
    dlg.Destroy()

def Warn(parent, message, caption = 'Warning'):
    dlg = wx.MessageDialog(parent, message, caption, wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()

# paths for installer
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'): # PyInstaller >= 1.6
        filename = os.path.join(sys._MEIPASS, filename)

    return filename


class MainWindow(wx.Frame):
  
    def __init__(self, parent, title):
        super(MainWindow, self).__init__(parent, title=title, size=(430, 350), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)

        self.InitUI()
        self.Centre()
        self.Show()  
  
    def InitUI(self):
    
        panel = wx.Panel(self)
        self.SetBackgroundColour('#292929')

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Directory:')
        st1.SetForegroundColour(wx.WHITE)
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc = wx.TextCtrl(panel)
        hbox1.Add(self.tc, proportion=1)
        btnDir = wx.Button(panel, label='...', size=(40, 20))
        hbox1.Add(btnDir, flag=wx.RIGHT, border=8)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        image = wx.ImageFromBitmap(wx.Bitmap(resource_path("BandeauDeletePadding2.png")))
        # image = image.Scale(195, 44, wx.IMAGE_QUALITY_HIGH)
        control = wx.StaticBitmap(panel, -1, wx.BitmapFromImage(image))
        hbox6.Add(control)
        vbox.Add(hbox6, flag=wx.LEFT, border=10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Log:')
        st2.SetForegroundColour(wx.WHITE)
        hbox2.Add(st2)
        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.tc2.SetBackgroundColour('#393939')
        self.tc2.SetForegroundColour(wx.WHITE)
        hbox3.Add(self.tc2, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, 
            border=10)

        vbox.Add((-1, 10))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        btnOk = wx.Button(panel, label='Ok', size=(70, 30))
        hbox5.Add(btnOk)
        btnClose = wx.Button(panel, label='Close', size=(70, 30))
        hbox5.Add(btnClose, flag=wx.LEFT|wx.BOTTOM, border=5)
        vbox.Add(hbox5, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        panel.SetSizer(vbox)


        # Setting up the menu
        filemenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Set event handlers
        self.Bind(wx.EVT_BUTTON, self.OnBtnDir, btnDir)
        self.Bind(wx.EVT_BUTTON, self.OnExit, btnClose)
        self.Bind(wx.EVT_BUTTON, self.OnBtnOk, btnOk)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)


    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Copyright AMFX 2013\n\nDeveloper: Arnaud Trouve\n\nwith the participation of\nMichael de Nicolo", "About Delete Padding", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBtnDir(self,e):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.tc.SetValue( dlg.GetPath() )
        dlg.Destroy()

    def OnBtnOk(self,e):

        # sanity checks
        pathDir = self.tc.GetValue()
        if not pathDir:
            Info(self, "Please enter a directory.","Delete Padding")
            return

        if not os.path.isdir(pathDir):
            Warn(self, "'" + pathDir + "' is not a valid directory.","Delete Padding")
            return

        self.tc2.SetValue("") # reinit
        txtLog = ""

        files = [f for f in listdir(pathDir) if isfile(join(pathDir,f)) ] # only files
        nbFiles = len(files)
        if(nbFiles <= 0):
            Info(self, "No file was found.","Delete Padding")
            return

        dlg = wx.ProgressDialog("Please wait", "Time remaining", int(nbFiles),
                 style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
        keepGoing = True
        cpt = 0
        cptRenamedFrames = 0

        for f in listdir(pathDir):
            if isfile(join(pathDir,f)):
                cpt += 1
                if(cpt < nbFiles): keepGoing = dlg.Update(cpt)

                filename = os.path.splitext(f)[0]
                ext = os.path.splitext(f)[1]

                arr = filename.split("_")
                if len(arr) > 1:
                    pattern = arr[len(arr)-1];
                    if pattern.isdigit():
                        newpattern = pattern.lstrip("0")
                        if len(newpattern) == 0: newpattern = "0"
                        if newpattern != pattern:
                            
                            newfilename = ""
                            cpt = 0
                            for a in arr:
                                newfilename += a + "_"
                                cpt += 1
                                if cpt == len(arr)-1:
                                    break

                            if not isfile( os.path.join(pathDir, newfilename + newpattern + ext ) ): # check file does not exist
                                cptRenamedFrames += 1
                                os.rename( os.path.join(pathDir, f), os.path.join(pathDir, newfilename + newpattern + ext ) )
                            else:
                                txtLog += "\nCould not rename " + f + " because " + newfilename + newpattern + ext + " already exists.\n"
                    
        self.tc2.SetValue("Done.\n" + str(nbFiles) + " frame(s) in directory, " + str(cptRenamedFrames) + " renamed frame(s).\n" + txtLog)
        dlg.Destroy()


    def OnExit(self,e):
        self.Close(True)  # Close the frame


if __name__ == '__main__':
  
    app = wx.App()
    MainWindow(None, title='Delete Padding')
    app.MainLoop()
