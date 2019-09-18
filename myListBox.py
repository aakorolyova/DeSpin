# copyright A. Koroleva and P. Paroubek
# LIMSI-CNRS

import sys

if sys.version_info[0] != 3:
    print( 'This script requires Python 3' )
    exit()

import tkinter as tki
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Frame, filedialog, Label, Button, Radiobutton, IntVar, StringVar, messagebox, Entry, Text, Scrollbar, Listbox


##By default, the selection is exported via the X selection mechanism
##(or the clipboard, on Windows). If you have more than one listbox on the screen,
##this really messes things up for the poor user. If she selects something in one
##listbox, and then selects something in another, the original selection disappears.
##It is usually a good idea to disable this mechanism in such cases.
##In the following example, three listboxes are used in the same dialog:
##
##b1 = Listbox(exportselection=0)
##for item in families:
##    b1.insert(END, item)
##
##b2 = Listbox(exportselection=0)
##for item in fonts:
##    b2.insert(END, item)
##
##b3 = Listbox(exportselection=0)
##for item in styles:
##    b3.insert(END, item)

def default_item_select_handler( e ):
    # e.x_root, e.y_root, e.num
    print( 'list box widget {0} has one click event is {1} at x= {2} y= {3}'.format( self.id,  e, e.x, e.y ) )
    s = self.list.curselection()
    print( s )
    items = map( int, self.list.curselection() )
    print( items )
    print( '-----------' )
    

class myListBox( Frame ):
    def __init__(self, root,  items = [], id = '', item_select_handler = default_item_select_handler, smode=tki.EXTENDED ):
        self.item_count = 0
        self.root = root
        self.item_select_handler = item_select_handler
        Frame.__init__( self, self.root )
        self.id = id
        vscrollbar = Scrollbar( self, orient=tki.VERTICAL)
        vscrollbar.pack( side=tki.RIGHT, fill=tki.Y )
        hscrollbar = Scrollbar( self, orient=tki.HORIZONTAL)
        hscrollbar.pack( side=tki.BOTTOM, fill = tki.X )
        ## mode can be: SINGLE, BROWSE, MULTIPLE, EXTENDED
        ##        selectmode
        ##
        ## Determines how many items can be selected, and how mouse drags affect the selection −
        ##
        ##    BROWSE − Normally, you can only select one line out of a listbox. If you click on an item and then drag to a different line, the selection will follow the mouse. This is the default.
        ##    SINGLE − You can only select one line, and you can't drag the mouse.wherever you click button 1, that line is selected.
        ##    MULTIPLE − You can select any number of lines at once. Clicking on any line toggles whether or not it is selected.
        ##    EXTENDED − You can select any adjacent group of lines at once by clicking on the first line and dragging to the last line.

        self.list = Listbox( self, selectmode = smode, exportselection = 0, xscrollcommand = hscrollbar.set, yscrollcommand = vscrollbar.set )
        for i in items:
            assert( type( i ) is str )
            self.list.insert( items.index(i), i )
        self.list.pack( fill=tki.BOTH, expand=1 )
        self.list.bind( '<Double-Button-1>', self.item_select_handler )
        self.list.bind( '<1>', self.item_select_handler )
        self.list.bind( '<Return>', self.item_select_handler )
        ## DO NOT catch ListboxSelect event, because:
        ##        a) it is not associated with (x_root, y_root) and (x,y) coordinates, so the popup appears always at (0,0) of the main root window
        ##        b) it duplicates the click event catching  self.list.bind( '<1>', self.item_select_handler ) and generates a second event
        ## self.list.bind( '<<ListboxSelect>>', self.item_select_handler )
        hscrollbar.config( command=self.list.xview )
        vscrollbar.config( command=self.list.yview )
        self.pack( side=tki.LEFT, fill=tki.BOTH, expand=1 )
        self.current = self.list.curselection()

    def insert_item( self, pos, item ):
        self.list.insert( pos, item )
        self.item_count += 1
        self.activate( pos )
        self.index( pos )
 
    def delete( self, start, end = None ):
        assert( type( start ) is int )
        if( end is None ):
            self.list.delete( start )
            self.item_count -= 1
        else:
            assert( (type( end ) is int) or (end == tki.END) )
            if( type( end ) is str ):
                self.list.delete( start, (self.item_count-1) )
                self.item_count -= (self.item_count - start) 
            else:
                self.list.delete( start, end )
                self.item_count -= (end - start) + 1

    def select_set( self, i ):
        self.list.selection_clear( 0, tki.END )
        self.list.select_set( i )

    def activate( self, i ):
        self.list.activate( i )

    def index( self, i ):
        self.list.index( i )

    def generate_select_event( self, pos = None ):
        assert( pos is not None )
        if( pos is not None ):
            self.activate( pos )
            self.index( pos )
            self.select_set( pos )
            self.list.event_generate( "<<ListboxSelect>>" )

##    def poll(self):
##        now = self.list.curselection()
##        if now != self.current:
##            self.list_has_changed( now )
##            self.current = now
##        self.after( 250, self.poll )

    def list_has_changed(self, selection):
        print( 'widget {0} selection is {1}'.format( self.id, selection  ))
##        self.item_select_handler()

##items=[ 'Python', 'Perl', 'C', 'PHP', 'JSP', 'Ruby', 'Pascal', 'Fortran', 'Modula', 'a very very very very lonnnnnnnnnnng programming language name', 'Spark', 'Haskell', 'Lisp', 'C++', 'Eiffel']
##items2=['foo', 'bar', 'zoo' ]
##root=tki.Tk()
##d1=myListBox( tki.Toplevel(), items, 'list_1')
##d2=myListBox( tki.Toplevel(), items2, 'list_2')
##root.mainloop()





