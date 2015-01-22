#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
 Name:
    Frame Recovery
 Version:
    1.0 (12 November 2013)
 Author:
    Arnaud Trouve (AMFX)
 Description:  
    List missing frames in an image sequence
 Usage:
    Select a directory, then "OK"
'''

import wx, os, re, sys, glob
from os import listdir
from os.path import isdir, isfile, join


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
        super(MainWindow, self).__init__(parent, title=title, size=(450, 420))
        self.InitUI()
        self.Centre()
        self.Show()  
  
    def InitUI(self):
    
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, label='Directory:')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc = wx.TextCtrl(panel)
        hbox1.Add(self.tc, proportion=1)
        btnDir = wx.Button(panel, label='...', size=(40, 20))
        hbox1.Add(btnDir, flag=wx.RIGHT, border=8)
        vbox.Add(hbox1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        self.cbSubfolders = wx.CheckBox(panel, label='Check subfolders   ')
        hbox4.Add(self.cbSubfolders, proportion=1)
        self.cbMissingFrames = wx.CheckBox(panel, label='Missing Frames')
        self.cbMissingFrames.SetValue(True)
        hbox4.Add(self.cbMissingFrames)
        self.cbEmptyFrames = wx.CheckBox(panel, label='Empty Frames - size min:')
        hbox4.Add(self.cbEmptyFrames, flag=wx.LEFT, border=10)
        self.tcSize = wx.TextCtrl(panel, -1, size=(40,20))
        self.tcSize.WriteText("0")
        hbox4.Add(self.tcSize)
        stKo = wx.StaticText(panel, label=' Ko')
        hbox4.Add(stKo)
        vbox.Add(hbox4, flag=wx.LEFT, border=10)

        vbox.Add((-1, 11))

        # hbox8 = wx.BoxSizer(wx.HORIZONTAL)
        # # self.cbSubfolders = wx.CheckBox(panel, label='Subfolders')
        # # hbox8.Add(self.cbSubfolders, proportion=1)
        # vbox.Add(hbox8, flag=wx.LEFT, border=10)

        # vbox.Add((-1, 20))

        hbox9 = wx.BoxSizer(wx.HORIZONTAL)
        self.cbSequence = wx.CheckBox(panel, label='Sequence:')
        hbox9.Add(self.cbSequence, flag=wx.ALIGN_BOTTOM, proportion=1)
        vbox.Add(hbox9, flag=wx.LEFT, border=10)

        vbox.Add((-1, 6))

        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        st7 = wx.StaticText(panel, label='In:')
        hbox7.Add(st7, flag=wx.RIGHT|wx.ALIGN_CENTER, border=8)
        self.tcMinFrame = wx.TextCtrl(panel, -1, size=(50,-1))
        self.tcMinFrame.WriteText("0")
        hbox7.Add(self.tcMinFrame, flag=wx.ALIGN_CENTER, proportion=1)
        st8 = wx.StaticText(panel, label='    Out:   ')
        # hbox7.Add(st8, flag=wx.RIGHT, border=8)
        hbox7.Add(st8, flag=wx.ALIGN_CENTER, border=8)
        self.tcMaxFrame = wx.TextCtrl(panel, -1, size=(50,-1))
        self.tcMaxFrame.WriteText("0")
        hbox7.Add(self.tcMaxFrame, flag=wx.ALIGN_CENTER, proportion=1)

        sttest = wx.StaticText(panel, label='        ') # FIXME: find sizer
        hbox7.Add(sttest)
        image = wx.ImageFromBitmap(wx.Bitmap(resource_path("FRAME_RecoveryTypo1.png")))
        image = image.Scale(195, 44, wx.IMAGE_QUALITY_HIGH)
        control = wx.StaticBitmap(panel, -1, wx.BitmapFromImage(image))
        hbox7.Add(control, flag=wx.TOP)
        vbox.Add(hbox7, flag=wx.LEFT, border=10)

        vbox.Add((-1, 5))

        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        st6 = wx.StaticText(panel, label='Delimiter:')
        hbox6.Add(st6, flag=wx.RIGHT, border=8)
        self.tcDelimiter = wx.TextCtrl(panel, -1, size=(20,-1))
        self.tcDelimiter.WriteText(",")
        hbox6.Add(self.tcDelimiter, proportion=1)

        stsizer = wx.StaticText(panel, label='        ')
        hbox6.Add(stsizer)
        # self.cbSubfolders = wx.CheckBox(panel, label='Subfolders')
        # hbox6.Add(self.cbSubfolders, proportion=1)
        vbox.Add(hbox6, flag=wx.LEFT, border=10)

        vbox.Add((-1, 10))

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(panel, label='Missing/Empty Frames:')
        hbox2.Add(st2)
        vbox.Add(hbox2, flag=wx.LEFT | wx.TOP, border=10)

        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.tcLog = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY|wx.TE_RICH)
        self.tcLog.SetBackgroundColour('#616161')
        self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
        hbox3.Add(self.tcLog, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)

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
        helpmenu= wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About","Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit","Terminate the program")
        menuHelp = helpmenu.Append(wx.ID_HELP,"&Help","Help about this program")

        # Creating the menubar
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"?")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Event handlers
        self.Bind(wx.EVT_BUTTON, self.OnBtnDir, btnDir)
        self.Bind(wx.EVT_BUTTON, self.OnExit, btnClose)
        self.Bind(wx.EVT_BUTTON, self.OnBtnOk, btnOk)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnHelp, menuHelp)


    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Copyright AMFX 2013\n\nDeveloper: Arnaud Trouve\n\nwith the participation of\nMichael de Nicolo\nMichael Jaffrain\nPierre Vincent", "About Frame Recovery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnHelp(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "1-Select a directory containing a frame sequence.\n2-Select 'Missing Frames' to display a list of images missing from the sequence.\n3- Select 'Empty Frames' to detect images whose size (in Kb) is inferior than the one specified.\n4-The 'delimiter' is the character used to concatenate the frame numbers in the exported list.", "Help Frame Recovery", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnBtnDir(self,e):
        dlg = wx.DirDialog(self, "Choose a directory:", "C:")
        if self.tc.GetValue(): dlg.SetPath( self.tc.GetValue() )

        if dlg.ShowModal() == wx.ID_OK:
            self.tc.SetValue( dlg.GetPath() )
        dlg.Destroy()

    def OnBtnOk(self,e):

        #---------------------------------------------------------------------------#
        # sanity checks
        #---------------------------------------------------------------------------#
        pathDir = self.tc.GetValue()
        if not pathDir:
            Info(self, "Please enter a directory.","Frame Recovery")
            return

        if not os.path.isdir(pathDir):
            Warn(self, "'" + pathDir + "' is not a valid directory.","Frame Recovery")
            return

        if not self.cbMissingFrames.IsChecked() and not self.cbEmptyFrames.IsChecked():
            Info(self,"Please select a checkbox.","Frame Recovery")
            return

        if self.cbSequence.IsChecked():
            if not self.tcMinFrame.GetValue().isnumeric() or not self.tcMaxFrame.GetValue().isnumeric():
                Warn(self, "Min/Max is not a number.","Frame Recovery")
                return

        if self.cbMissingFrames.IsChecked() and self.cbEmptyFrames.IsChecked():
            if not self.tcSize.GetValue().isnumeric():
                Warn(self, "Size/Min/Max is not a number.","Frame Recovery")
                return
        elif self.cbEmptyFrames.IsChecked():
            if not self.tcSize.GetValue().isnumeric():
                Warn(self, "Size is not a number.","Frame Recovery")
                return

        lastNb, fileName, extension, imageName = "", "", "", ""
        i, cpt, cptMygale, nbSubDirs, nbFilesTotalReal, maxLastNb, minFrame, maxFrame, nbZeros = 2, 0, 0, 0, 0, 0, 0, 0, 0
        theList, listFrames, listMissingFrames, listMF2, listEmptyFrames, listEF2 = [], [], [], [], [], []

        if self.cbSequence.IsChecked():
            minFrame = int(self.tcMinFrame.GetValue())
            maxFrame = int(self.tcMaxFrame.GetValue())


        #---------------------------------------------------------------------------#
        # find last frame in subdirectories (ignore other files. files are sorted by name, by default)
        #---------------------------------------------------------------------------#
        if self.cbSubfolders.IsChecked():
            for d in listdir(pathDir):
                if isdir(join(pathDir,d)):
                    nbSubDirs += 1
                    subdirpath = os.path.join(pathDir, d)
                    files = [f for f in listdir(subdirpath) if isfile(join(subdirpath,f)) ] # only files
                    nbFiles = len(files)
                    if(nbFiles > 0):
                        nbFilesTotalReal += nbFiles
                        fileName = os.path.splitext(files[nbFiles-1])[0]
                        extension = os.path.splitext(files[nbFiles-i])[1] # .png

                        test = fileName.split("_")[-1]
                        if test.isdigit():
                            tmpLastNb = int(re.sub("^0+","",test))
                            if tmpLastNb > maxLastNb:
                                maxLastNb = tmpLastNb
                                arr = fileName.split("_") # [B14,Render,Stroke,Cam01,4000Frame,0000037]
                                nbZeros = len(arr[-1]) # 7
                                arr.pop() # [B14,Render,Stroke,Cam01,4000Frame]
                                imageName = "_".join(arr) + "_"

            if maxFrame == 0: maxFrame = maxLastNb + 1

            #---------------------------------------------------------------------------#
            # loop on frames
            #---------------------------------------------------------------------------#
            self.tcLog.SetValue("") # reinit
            self.tcLog.WriteText("##### RESULT PROCESSING #####\n\n")
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText("Folder directories: ") 
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( os.path.split(pathDir)[1] )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\nSubfolders parsed: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(nbSubDirs) )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\n\nTotal Frames: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(nbFilesTotalReal) )

            nbFilesTotal = nbSubDirs * (int(maxFrame) - int(minFrame))
            dlg = wx.ProgressDialog("Please wait", "Time remaining", int(nbFilesTotal),
                     style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
            keepGoing = True

            for d in listdir(pathDir):
                if isdir(join(pathDir,d)):
                    subdirpath = os.path.join(pathDir, d)

                    # create frame lists
                    for nb in range(minFrame,int(maxFrame)):
                        cpt += 1
                        keepGoing = dlg.Update(cpt)

                        theImagePath = subdirpath + "\\" + imageName;
                        for i in range( nbZeros - len(str(nb)) ): theImagePath += "0"
                        theImagePath += str(nb) + extension

                        if not os.path.exists(theImagePath):
                            listMF2.append(nb)                                
                            if not nb in listFrames: listFrames.append(nb)
                            if not nb in listMissingFrames: listMissingFrames.append(nb)
                        elif os.path.getsize(theImagePath) < 1024 * int(self.tcSize.GetValue()):
                            listEF2.append(nb)                                
                            if not nb in listFrames: listFrames.append(nb)
                            if not nb in listEmptyFrames: listEmptyFrames.append(nb)

            listFrames.sort()
            listMissingFrames.sort()
            listEmptyFrames.sort()

        #---------------------------------------------------------------------------#
        # find last frame in directory (ignore other files. files are sorted by name, by default)
        #---------------------------------------------------------------------------#
        else:

            files = [f for f in listdir(pathDir) if isfile(join(pathDir,f)) ] # only files
            nbFiles = len(files)
            if(nbFiles <= 0):
                Info(self, "No file was found in this directory.","Frame Recovery")
                return

            while not lastNb.isdigit():
                if( i-2 == nbFiles): # no more file to parse
                    Info(self, "No frame was found in this directory.","Frame Recovery")
                    return

                if len(os.path.splitext(files[nbFiles-i])) > 1:
                    fileName = os.path.splitext(files[nbFiles-i])[0] # B14_Render_Stroke_Cam01_4000Frame_0000037
                    extension = os.path.splitext(files[nbFiles-i])[1] # .png
                    arr = fileName.split("_") # [B14,Render,Stroke,Cam01,4000Frame,0000037]
                    lastNb = arr[-1] # 0000037

                i += 1

            nbZeros = len(lastNb) # 7
            lastNb = re.sub("^0+","",lastNb) # 37
            arr.pop() # [B14,Render,Stroke,Cam01,4000Frame]
            imageName = "_".join(arr) + "_"

            if maxFrame == 0: maxFrame = lastNb

            #---------------------------------------------------------------------------#
            # loop on frames
            #---------------------------------------------------------------------------#
            self.tcLog.SetValue("") # reinit
            # self.tcLog.WriteText("##### RESULT PROCESSING #####\n\nDirectory: " + os.path.split(pathDir)[1] + "\n\nTotal Frames: " + str(nbFiles))
            self.tcLog.WriteText("##### RESULT PROCESSING #####\n\n")
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText("Directory: ") 
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( os.path.split(pathDir)[1] )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\n\nTotal Frames: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(nbFilesTotalReal) )

            dlg = wx.ProgressDialog("Please wait", "Time remaining", int(maxFrame),
                     style=wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)
            keepGoing = True

            # create frame lists
            for nb in range(minFrame,int(maxFrame)):
                cpt += 1
                keepGoing = dlg.Update(cpt)

                theImagePath = pathDir + "\\" + imageName;
                for i in range( nbZeros - len(str(nb)) ): theImagePath += "0"
                theImagePath += str(nb) + extension
                if not os.path.exists(theImagePath):
                    listMissingFrames.append(nb)
                    listFrames.append(nb)
                elif os.path.getsize(theImagePath) < 1024 * int(self.tcSize.GetValue()):
                    listEmptyFrames.append(nb)
                    listFrames.append(nb)


        #---------------------------------------------------------------------------#
        # display results
        #---------------------------------------------------------------------------#

        if self.cbMissingFrames.IsChecked() and self.cbEmptyFrames.IsChecked():
            theList = listFrames
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\nMissing: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(len(listMissingFrames)) )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\nEmpty: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(len(listEmptyFrames)) )

            if len(theList) > 0:
                self.tcLog.WriteText( "\n\n\tMissing\tEmpty" )
                if self.cbSubfolders.IsChecked() : self.tcLog.WriteText("\tMissing Count")
                self.tcLog.WriteText( "\n")

                for x in theList:
                    self.tcLog.WriteText(str(x) + "\t")
                    if x in listMissingFrames:

                        self.tcLog.SetDefaultStyle(wx.TextAttr(wx.RED));
                        if self.cbSubfolders.IsChecked():
                            self.tcLog.WriteText("X")
                        else:
                            self.tcLog.WriteText("X")

                        self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));

                    else:
                        self.tcLog.WriteText("\t")
                        self.tcLog.SetDefaultStyle(wx.TextAttr(wx.GREEN));
                        self.tcLog.WriteText("-")
                        self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));

                    if x in listEmptyFrames:

                        self.tcLog.WriteText("\t")
                        if self.cbSubfolders.IsChecked():
                            self.tcLog.WriteText( str(listEF2.count(x)) )
                        else:
                            self.tcLog.WriteText("X")

                    else:
                        self.tcLog.WriteText("\t-")

                    if self.cbSubfolders.IsChecked():
                        if listMF2.count(x) == nbSubDirs: self.tcLog.SetDefaultStyle(wx.TextAttr(wx.RED));
                        self.tcLog.WriteText( "\t" + str(listMF2.count(x)) )
                        if listMF2.count(x) == nbSubDirs: self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
                    self.tcLog.WriteText( "\n")

        elif self.cbMissingFrames.IsChecked():

            theList = listMissingFrames
            if self.cbSubfolders.IsChecked():
                self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
                self.tcLog.WriteText( "\nMissing: " )
                self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
                self.tcLog.WriteText( str(len(listMF2)) + "\n\n" )

                self.tcLog.WriteText( "\n\nMissing\tMissing Count\n")
                for x in theList:
                    self.tcLog.WriteText( str(x) )
                    if listMF2.count(x) == nbSubDirs: self.tcLog.SetDefaultStyle(wx.TextAttr(wx.RED));
                    self.tcLog.WriteText( "\t" + str(listMF2.count(x)) + "\n")
                    if listMF2.count(x) == nbSubDirs: self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));

            else:
                self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
                self.tcLog.WriteText( "\nMissing: " )
                self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
                self.tcLog.WriteText( str(len(theList)) + "\n\n" )
                for x in theList: self.tcLog.WriteText(str(x) + "\n")

        elif self.cbEmptyFrames.IsChecked():
            theList = listEmptyFrames
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.BLACK));
            self.tcLog.WriteText( "\nEmpty Frames: " )
            self.tcLog.SetDefaultStyle(wx.TextAttr(wx.WHITE));
            self.tcLog.WriteText( str(len(theList)) + "\n\n" )
            if self.cbSubfolders.IsChecked():
                for x in theList: self.tcLog.WriteText( str(x) + " (empty " + str(listEF2.count(x)) + ")" + "\n" )
            else:
                for x in theList: self.tcLog.WriteText(str(x) + "\n")

        self.tcLog.WriteText( "\n\nMygale lsf/lance.bat:\n" )
        if len(theList) == 0: self.tcLog.WriteText("<empty>")
        else:
            for x in theList:
                if( cptMygale % 40 == 0 ): self.tcLog.WriteText("\n")
                self.tcLog.WriteText(str(x))
                if( cptMygale < len(theList)-1 ): self.tcLog.WriteText( self.tcDelimiter.GetValue() )
                cptMygale += 1

        dlg.Destroy()


    def OnExit(self,e):
        self.Close(True)  # Close the frame


if __name__ == '__main__':
  
    app = wx.App()
    MainWindow(None, title='Frame Recovery')
    app.MainLoop()
