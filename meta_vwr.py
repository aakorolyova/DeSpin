# copyright A. Koroleva and P. Paroubek
# LIMSI-CNRS

import sys
import os

if sys.version_info[0] != 3:
    print( 'This script requires Python 3' )
    exit()

import tkinter as tki
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Frame, Label, IntVar, StringVar, messagebox, Text, Scrollbar


class meta_vwr():
    def __init__(self, master, x=None, y=None ):
        self.master_app = master
        self.meta_vwr_root = tki.Toplevel()
        self.meta_vwr_root.title( 'metadata editor' )
        self.meta_vwr_root.protocol( "WM_DELETE_WINDOW", self.__del__ )
        scrn_w = self.master_app.root.winfo_screenwidth()
        width = scrn_w/3
        if( x is None ):
            x = (scrn_w/3) - (width/3)
        scrn_h = self.master_app.root.winfo_screenheight()
        height = scrn_w/3
        if( y is None ):
            y = (scrn_h/3) - (height/3)
        self.meta_vwr_root.geometry('%dx%d+%d+%d' % (width, height, x, y))

        self.meta_vwr_frame = tki.Frame( self.meta_vwr_root )
        self.meta_vwr_frame.pack( side='bottom', fill='both', expand=True )
        
        self.textPad = ScrolledText(  self.meta_vwr_frame, wrap='word', undo=True )
        self.textPad['font'] = ('consolas', '12')
        self.textPad.pack( side='left', fill='both', expand=True )
        self.textPad.config( state='normal' )
        self.textPad.delete('1.0', tki.END )
        self.textPad.insert( 1.0, self.master_app.doc.meta )
        self.old_metadata = self.master_app.doc.meta

        self.meta_vwrmenu = tki.Menu( self.meta_vwr_root, tearoff=0 )
        self.meta_vwr_root.config( menu=self.meta_vwrmenu )
        self.meta_vwrmenu.add_command( label="Undo", underline=1, command=self.undo_handler )
        self.meta_vwrmenu.add_command( label="Redo", underline=1, command=self.redo_handler )
        self.meta_vwrmenu.add_command( label="Delete All", underline=1, command=self.delete_all_handler )
        self.meta_vwrmenu.add_command( label="Cancel", underline=1, command=self.cancel_handler )
        
        self.master_app.meta_vwr = self
        print( 'init meta_vwr master_meta_vwr is {0}'.format( self.master_app.meta_vwr ))
        self.meta_vwr_root.update_idletasks()
        self.meta_vwr_root.mainloop()

    def __del__( self ):
        self.meta_vwr_root.update_idletasks()
        self.meta_vwr_root.quit()
        self.meta_vwr_root.destroy()
        self.master_app.meta_vwr = None
        print( 'deleted meta vwr master meta_vwr is {0}'.format( self.master_app.meta_vwr ))

    def undo_handler( self, event=None ):
        self.textPad.edit_undo()
        
    def redo_handler( self, event=None ):
        self.textPad.edit_redo()

    def delete_all_handler( self ):
        self.textPad.delete('1.0', tki.END )

    def cancel_handler( self ):
        self.master_app.doc.meta = self.textPad.get( '1.0', tki.END + '-1c' )
        self.__del__()

    def refresh_handler( self ):
        print( 'meta_vwr refresh master_app_meta_vwr={0}'.format( self.master_app.meta_vwr ))
        self.meta_vwr_root.lift()
        self.meta_vwr_root.update_idletasks()
        
        
            
