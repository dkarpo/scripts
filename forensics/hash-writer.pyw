#!/usr/bin/python
#
# A crude script to read file(s) and write out a <filename>.<hash>.txt
# file for each selected hash.  Requires wxPython.
#
# Author: Derrick Karpo
# Date:   February 5, 2013
#

import sys
import wx
import hashlib


class FileDropTarget(wx.FileDropTarget):
   def __init__(self, obj):
      wx.FileDropTarget.__init__(self)
      self.obj = obj

   def OnDropFiles(self, x, y, filenames):
      self.obj.SetInsertionPointEnd()

      for fn in filenames:
         # open the file and start hashing
         self.obj.WriteText("Hashing '%s'..." % fn)
         try:
            with open(fn, 'rb') as f:
               # hashes to run
               md5hash = hashlib.md5()
               sha1hash = hashlib.sha1()
               sha256hash = hashlib.sha256()

               while True:
                  b = f.read(8192)
                  if not b:
                     break
                  md5hash.update(b)
                  sha1hash.update(b)
                  sha256hash.update(b)

            self.obj.WriteText("complete." + '\n')
         except:
            self.obj.WriteText("Hashing failed for: '%s'.  Exiting." % fn)

         # write the output files
         try:
            # write the MD5 hash
            self.obj.WriteText("Writing MD5 hash '%s.md5.txt'..." % fn)
            fout = open(fn + '.md5.txt', 'w')
            fout.write(md5hash.hexdigest() + '\n')
            fout.close()
            self.obj.WriteText('complete.' + '\n')

            # write the SHA1 hash
            self.obj.WriteText("Writing SHA1 hash '%s.sha1.txt'..." % fn)
            fout = open(fn + '.sha1.txt', 'w')
            fout.write(sha1hash.hexdigest() + '\n')
            fout.close()
            self.obj.WriteText('complete.' + '\n')

            # write the SHA256 hash
            self.obj.WriteText("Writing SHA256 hash '%s.sha256.txt'..." % fn)
            fout = open(fn + '.sha256.txt', 'w')
            fout.write(sha256hash.hexdigest() + '\n')
            fout.close()
            self.obj.WriteText('complete.' + '\n')

            # all done
            self.obj.WriteText('\n')
         except:
            self.obj.WriteText("Writing output hashes failed for: '%s'.  Exiting." % fn)


class MainWindow(wx.Frame):
   def __init__(self, parent, id, title):
      wx.Frame.__init__(self, None, wx.ID_ANY, title,
                        size = (900,300), style=wx.DEFAULT_FRAME_STYLE &
                        ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER))

      # menu
      menuBar = wx.MenuBar()
      filemenu = wx.Menu()
      menuAbout = filemenu.Append(wx.ID_ABOUT, "&About")
      filemenu.AppendSeparator()
      menuExit = filemenu.Append(wx.ID_EXIT,"E&xit")
      menuBar.Append(filemenu, "&File")
      filemenu = wx.Menu()
      self.SetMenuBar(menuBar)

      # events
      self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
      self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

      # GUI widgets
      self.banner = wx.TextCtrl(self, -1, "Drag and drop file(s) to the above space then have patience young padawan...patience.", pos=(1,215), size=(891,30), style = wx.TE_CENTRE|wx.TE_READONLY)
      self.dropzone = wx.TextCtrl(self, -1, "", pos=(1,1), size=(891,210), style = wx.TE_MULTILINE|wx.TE_READONLY)
      dt1 = FileDropTarget(self.dropzone)
      self.dropzone.SetDropTarget(dt1)

      # display the window
      self.Show(True)

   def OnClose(self, event):
      self.Close()

   def OnDragInit(self, event):
       tdo = wx.PyTextDataObject(self.text.GetStringSelection())
       tds = wx.DropSource(self.text)
       tds.SetData(tdo)
       tds.DoDragDrop(True)

   def OnAbout(self, event):
      dlg = wx.MessageDialog(
         self, "Hash Writer\n\n"
         "MD5, SHA1, and SHA256 hash files, then write the hash\n"
         "values out to similarily named but separate text files.",
         "About", wx.OK)
      dlg.ShowModal()
      dlg.Destroy()

   def OnExit(self, event):
      self.Close(True)


class MainApp(wx.App):
   def OnInit(self):
      frame = MainWindow(None, -1, "Hash Writer")
      self.SetTopWindow(frame)
      return True


app = MainApp(0)
app.MainLoop()
