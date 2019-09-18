# copyright A. Koroleva and P. Paroubek
# LIMSI-CNRS

import sys
import os
import codecs

if sys.version_info[0] != 3:
    print( 'This script requires Python 3' )
    exit()

import tkinter as tki
from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Frame, filedialog, Label, Button, Radiobutton, IntVar, StringVar, messagebox, Entry, Text, Scrollbar, Listbox

from namelistmap import namelistmap

from myListBox import myListBox

from tkinter import *

import tkinter.colorchooser
from tkinter.colorchooser import askcolor

from text_span import  mwu, rel, construction, document

from Samer import SFRel
     
from preannotation import Annotate

from namespace import namespace

from meta_vwr import meta_vwr

my_config_path = 'ak_pc_construkt.cfg'

#-------- tkinter specific utility functions and classes (what is the model part in a model-view-controler architecture) -------------
def tk_add_to_num_pair( a ):
    #converts a string of the form '7.555', 7=line number  555=char offset in the line
    # to a pair of integer (7 , 555)
    aux = a.split( '.' )
    assert( len( aux ) == 2 )
    return ( int(aux[0]), int(aux[1]) )
    
def intersects( wnts_list, f, l ):
    # return True if the widget text span delimited by f=first and l=last,
    # instersects any of the list of widget text spans of wnts_list,
    # and false otherwise.
    f_add = tk_add_to_num_pair( f )
    l_add = tk_add_to_num_pair( l )
    for w in wnts_list:
        w_first_add = tk_add_to_num_pair( w.first )
        w_last_add = tk_add_to_num_pair( w.last )
        if( ((w_first_add <= f_add) and (f_add < w_last_add)) ): 
            return True
        if( ((w_first_add < l_add) and (l_add <= w_last_add)) ):
            return True
        if( ((f_add < w_first_add) and (w_first_add <= l_add)) ):
            return True
        if( ((f_add < w_last_add) and (w_last_add <= l_add)) ):
            return True
    return False

def multi_intersects( wnts_list1, wnts_list2 ):
    # return True if the widget text span delimited by f=first and l=last,
    # instersects any of the list of widget text spans of wnts_list,
    # and false otherwise.
    for w in wnts_list2:
        if( intersects( wnts_list1, w.first, w.last )):
            return True
    return False

def equal_span_and_type( wnts_list1, wnts_list2 ):
    i = 0
    for w in wnts_list2:
        if( (wnts_list1[ i ].first != w.first ) or (wnts_list1[ i ].last != w.last ) or (wnts_list1[ i ].typ != w.typ)):
            return False
        i += 1
    return True

# tkinter named character text span for the ScrolledText widget (duplicates the widget internal representation of named span)
class wnts(object):
    # widget named text span
    def __init__( self, i, f, l, text_widget=None, typ = None, foreground='black', background='white' ):
##        print( 'creating wnts with i={0} f={1} l={2} text_widget={3} typ={4}'.format( i, f, l, text_widget, typ ))
##        print( 'creatwnts argtypes i={0} f={1} l={2} text_widget={3} typ={4}'.format( type(i), type(f), type(l), type(text_widget), type(typ) ))
        self.id = str( i )
        assert( (type( f ) is str) and (type(eval(f)) is float))
        assert( (type( l ) is str) and (type(eval(l)) is float))
        self.first = f   # 'line_pos.col_pos' = index of the text position before the first char, i.e. a string of the form 'line_nbr.char_pos_nbr'
        self.last = l    # 'line_pos.col_pos' = index of the text position after the last char,   i.e. a string of the form 'line_nbr.char_pos_nbr'
        self.txtwid = text_widget
        self.typ = str( typ )
        self.fg = foreground
        self.bg = background
        self.show()

    def __del__( self ):
        if( self.id in self.txtwid.tag_names()):
            self.txtwid.tag_delete( self.id )
##        print( '--->__del__() wnts id= {0}\n\ttag_names={1}\n\t mark_nams={2}'.format( self.id, self.txtwid.tag_names(), self.txtwid.mark_names()) )

    def __repr__( self ):
        return( '<wnts: ' + self.id + ':' + self.typ  + ', ' +  self.first  + ', ' +  self.last  + '>' ) 

    def __str__( self ):
        print( 'wnts str type i={0} f={1} l={2} text_widget={3} typ={4}'.format( type(self.id), type(self.first), type(self.last),
                                                                                 type(self.txtwid), type(self.typ) ))
        sout = 'wnts: name= ' + self.id + 'type= ' + self.typ + ' first= ' +  self.first  + ' last= ' +  self.last + '\n'
        return( sout )

    def set_type( self, typ ):
        assert( type( typ ) is str )
        self.typ = typ

    def show( self ):
        if( self.txtwid is not None ):
            all_tags = self.txtwid.tag_names()
            if( self.id not in all_tags ):
                self.txtwid.tag_add( self.id, self.first, self.last )
            self.txtwid.tag_config( self.id, foreground = self.fg, background = self.bg )
##        print( '--->SHOW() wnts id= {0} \n\ttag_names={1}\n\t mark_nams={2}'.format( self.id, self.txtwid.tag_names(), self.txtwid.mark_names()) )

    def hide( self ):
        if( self.txtwid is not None ):
            all_tags = self.txtwid.tag_names()
            if( self.id in all_tags ):
                self.txtwid.tag_delete( self.id )
##        print( '--->HIDE() wnts id= {0}\n\ttag_names={1}\n\t mark_nams={2}'.format( self.id, self.txtwid.tag_names(), self.txtwid.mark_names()) )

    def color( self, fg=None, bg=None ):
##         print( '--->COLOR() wnts id= {0} color() fg={1} bg={2}\n'.format( self.id, fg, bg))
         if( fg is not None ):
            self.fg = fg
         if( bg is not None ):
            self.bg = bg
         self.show()

# replaced all this by a specific quick-sort-function because the following comparison functions generate an error:
##Exception in Tkinter callback
##Traceback (most recent call last):
##  File '/usr/lib/python3.5/tkinter/__init__.py', line 1553, in __call__
##    return self.func(*args)
##  File '/media/pap/HDTOSHIBA1T/work/MIROR/TOOLS/python/constructions/cg2/py', line 264, in last_src_text_span_handler
##    self.all_spans.set( mltspan_nm, self.curr_span_wnts_lst )
##  File '/media/pap/HDTOSHIBA1T/work/MIROR/TOOLS/python/constructions/cg2/namelistmap.py', line 102, in set
##    uniq_itemlist = list( set( itemlist ))
##TypeError: unhashable type: 'wnts'
##>>> 
##    def __eq__( self, other ):
##        # Note: it is not taken into account in the comparison
##        return( (self.first == other.first) and (self.last == other.last))
##
##    def __lt__( self, other ):
##        return( (self.first < other.first) or (self.last < other.last) )
##
##    def __le__( self, other ):
##        return( (self.first <= other.first) or (self.last <= other.last) )
##
##    def __gt__( self, other ):
##        return( (self.last > other.last) or ( self.first > other.first) )
##
##    def __ge__( self, other ):
##         return( (self.last >= other.last) or ( self.first >= other.first) )

    def is_less_than( self, other ):
         return( (float( self.first) < float( other.first)) or (float( self.last) < float( other.last)) )

    def is_equal( self, other ):
        return( (float( self.first) == float( other.first)) and (float( self.last) == float( other.last)))
 
#---end of class wnts -------------

def wnts_lst_select_less( l, v, less, eql, greater ):
    for w in l:
        if w.is_less_than( v ):
            less.append( w )
        else:
            if( w.is_equal( v )):
                eql.append( w )
            else:
                greater.append( w )
    return( less, eql, greater )

def wnts_lst_quicksort( l ):
    if( l == [] ):
        # print( 'debugA')
        return []
    else:
        if( len( l ) == 1 ):
                # print( 'debugB')
                return( l )
        else:
            if( len( l ) == 2 ):
               if( l[0].is_less_than( l[1] )):
                   # print( 'debugC')
                   return( [l[0], l[1]] )
               else:
                  #print( 'debugD')
                  return( [l[1], l[0]] )         
            else:
                (lss, eql, gtr) = wnts_lst_select_less( l, l[len(l)//2], [], [], [] )
                # print( 'lss={0}\neql={1}\ngtr={2}'.format( lss, eql, gtr) )
                if( gtr == [] ):
                    if( lss == [] ):
                        # print( 'debugE')
                        return( eql )
                    else:
                        # print( 'debugF')
                        return( wnts_lst_quicksort( lss ) + eql )
                else:
                    if( lss == [] ):
                        # print( 'debugG')
                        return( eql + wnts_lst_quicksort( gtr ) )
                    else:
                        #print( 'debugH')
                        return( wnts_lst_quicksort( lss ) + eql + wnts_lst_quicksort( gtr ) )
                         
#--------- end of tkinter utilities -------------------------------------------------------------

class mwu_viewer( object ):
    def __init__( self, construkt_app, x=None, y=None ):
        self.master_app = construkt_app
        self.all_spans_listbox_indices = {} # associates to each mwu_span key in self.master_app.all_spans its index in the ListBox as its key in self.all_spans_listbox_indices
        self.fgcolor = self.master_app.mwu_fg_color
        self.bgcolor = self.master_app.mwu_bg_color
        self.master_app.all_mwu_root = tki.Toplevel()
        self.master_app.all_mwu_root.title( 'show all mwu' )
        self.master_app.all_mwu_root.protocol( "WM_DELETE_WINDOW", self.master_app.show_mwu_cancel_handler )
        scrn_w = self.master_app.root.winfo_screenwidth()
        width = scrn_w/3
        if( x is None ):
            x = (scrn_w/3) - (width/3)
        scrn_h = self.master_app.root.winfo_screenheight()
        height = scrn_w/3
        if( y is None ):
            y = (scrn_h/3) - (height/3)
        self.master_app.all_mwu_root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        # width in characters and height in lines
        # STANDARD OPTIONS
        ##        background, borderwidth, cursor,
        ##        exportselection, font, foreground,
        ##        highlightbackground, highlightcolor,
        ##        highlightthickness, insertbackground,
        ##        insertborderwidth, insertofftime,
        ##        insertontime, insertwidth, padx, pady,
        ##       relief, selectbackground,
        ##        selectborderwidth, selectforeground,
        ##  xscrollcommand, yscrollcommand,
##        self.mwu_listbox = myListBox( self.master_app.all_mwu_root, [], 'mwu_viewer', lambda e : self.mwu_listbox.item_select_handler )
        self.mwu_listbox = myListBox( self.master_app.all_mwu_root, [], 'mwu_viewer', lambda e : self.mwu_selection_handler( e ) )
        self.refresh()
        #Button( master=self.master_app.all_mwu_root, text='Cancel', command=self.master_app.show_mwu_cancel_handler).pack(side='left')
        self.master_app.all_mwu_root.all_mwu_menu = tki.Menu( self.master_app.all_mwu_root )
        self.master_app.all_mwu_root.config( menu=self.master_app.all_mwu_root.all_mwu_menu )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Cancel',command=self.master_app.show_mwu_cancel_handler )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Refresh', command=self.master_app.show_mwu_refresh_handler )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Show All', command=self.show_all_mwus_handler )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Clear View', command=self.master_app.show_mwu_clear_view_handler )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Set Background', command = self.set_bgcolor )
        self.master_app.all_mwu_root.all_mwu_menu.add_command( label='Set Foreground', command = self.set_fgcolor )
        self.master_app.all_mwu_root.all_mwus_on_display = True
        #----- popup menu for mwus ---
        self.popup_menu = tki.Menu( self.mwu_listbox, tearoff=0 )
        self.popup_menu.add_command( label='Show', command=self.mwu_show_handler )
        self.popup_menu.add_command( label='Hide', command=self.mwu_hide_handler  )
        self.popup_menu.add_command( label='Done', command=self.mwu_done_handler )
        self.popup_menu.add_command( label='Delete', command=self.mwu_delete_handler  )

    def set_bgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.bgcolor = hexstr

    def set_fgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.fgcolor = hexstr
        
    def draw( self ):
        all_mwu_repr = []
        n = 0
        self.all_spans_listbox_indices = {}
        for k in self.master_app.all_spans.get_all_keys():
            curr_mwu_repr = '{0} '.format( repr( k ) ).replace( '\'', '')
            self.all_spans_listbox_indices[ n ] = k
            n += 1
            for wnt in wnts_lst_quicksort( self.master_app.all_spans.get( k )):
                # to have all the text in one line in order to use the mwu_textPad lines as index for mwu selection
                flpos,fcpos = self.master_app.coordinates( wnt.first )
                llpos,lcpos = self.master_app.coordinates( wnt.last ) 
                txtsp = self.master_app.textPad.get( wnt.first, wnt.last ).replace( '\n', ' ')
                curr_mwu_repr += ' {0} <L_{1}, C_{2}>{3}<L_{4},C_{5}>'.format( wnt.typ, flpos, fcpos, txtsp, llpos, lcpos )
            all_mwu_repr.append( curr_mwu_repr )
        self.mwu_listbox.delete( 0, tki.END )
        for i in all_mwu_repr:
            self.mwu_listbox.insert_item( all_mwu_repr.index(i), i )
        self.master_app.all_mwu_root.lift()

    def mwu_selection_handler( self, e = None ):
        assert( e is not None )
        self.popup_menu.post( e.x_root, e.y_root )

    def show_all_mwus_handler( self, e = None):
        for i in range( 0, len( self.master_app.all_spans.get_all_keys() )):
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.all_spans_listbox_indices[ i ]),
                                         bgcol=self.bgcolor,
                                         fgcol=self.fgcolor )
        self.refresh()
        
    def mwu_show_handler( self, e = None ):
        items = map( int, self.mwu_listbox.list.curselection() )
        for i in items:
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.all_spans_listbox_indices[ i ]),
                                         bgcol=self.bgcolor,
                                         fgcol=self.fgcolor )
##  the following code does not do anything (no scroll at all to the displayed position).
##        if( len( list(items) ) > 0 ):
##            # move the text cursor to the first mwu and scroll the text window if necessary
##            m = self.master_app.all_spans.get( self.all_spans_listbox_indices[ 0 ] )
##            self.master_app.textPad.see( self.master_app.text_widget_line_idx(  m.first ) + '.' + self.master_app.text_widget_col_idx(  m.first ) )
        self.refresh()

    def mwu_hide_handler( self, e = None ):
        items = map( int, self.mwu_listbox.list.curselection() )
        for i in items:
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.all_spans_listbox_indices[ i ] ))
        self.refresh()

    def mwu_done_handler( self, e = None ):
        #print( 'mwu done handler == NOP' )
        self.refresh()

    def mwu_delete_handler( self, e = None ):
        items = map( int, self.mwu_listbox.list.curselection() )
        for i in items:
            mid = self.all_spans_listbox_indices[ i ]
            self.master_app.remove_referring_rels( mid )
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( mid ) )
            self.master_app.all_spans.remove( nm=self.all_spans_listbox_indices[ i ] )
            self.mwu_listbox.delete( i )
        self.refresh()
        if( self.master_app.rel_vwr is not None ):
            self.master_app.rel_vwr.refresh()
        
    def run( self ):
        self.master_app.all_mwu_root.mainloop()

    def __del__( self ):
        if( self.master_app.all_mwu_root is not None ):
            self.master_app.all_mwu_root.quit()
            self.master_app.all_mwu_root.destroy()
            self.master_app.all_mwu_root = None
            self.master_app.mwu_vwr = None

    def refresh( self ):
        # this will provoke the death of this instance and the creation of a new instance of this class through a call to a handler of the master app.
        #self.master_app.show_mwu_cancel_handler()
        #self.master_app.mwu_vwr = self.master_app.mwu_handler()
        self.draw()
        #self.master_app.root.update_idletasks()
        self.master_app.root.update()

    def clear_view( self ):
        for k in self.all_spans_listbox_indices.keys():
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.all_spans_listbox_indices[ k ] ) )

#---- end of class mwu_viewer =================================================================

class rel_viewer( object ):
    def __init__( self, construkt_app, x=None, y=None ):
        self.master_app = construkt_app
        self.master_app.selected_rel_lst = []
        self.all_rels_listbox_indices = {} # associates to each relation key in self.master_app.all_rels its index in the ListBox as its key in self.all_spans_listbox_indices
        self.src_fgcolor = self.master_app.fg_src_color
        self.src_bgcolor = self.master_app.bg_src_color
        self.trgt_fgcolor = self.master_app.fg_trgt_color
        self.trgt_bgcolor = self.master_app.bg_trgt_color 
        self.master_app.all_rel_root = tki.Toplevel()
        self.master_app.all_rel_root.title( 'show all relations' )
        self.master_app.all_rel_root.protocol( "WM_DELETE_WINDOW", self.__del__ )
        scrn_w = self.master_app.root.winfo_screenwidth()
        width = scrn_w/3
        if( x is None ):
            x = (scrn_w/3) - (width/3)
        scrn_h = self.master_app.root.winfo_screenheight()
        height = scrn_w/3
        if( y is None ):
            y = (scrn_h/3) - (height/3)
        self.master_app.all_rel_root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        # width in characters and height in lines
        # STANDARD OPTIONS
        ##        background, borderwidth, cursor,
        ##        exportselection, font, foreground,
        ##        highlightbackground, highlightcolor,
        ##        highlightthickness, insertbackground,
        ##        insertborderwidth, insertofftime,
        ##        insertontime, insertwidth, padx, pady,
        ##       relief, selectbackground,
        ##        selectborderwidth, selectforeground,
        ##  xscrollcommand, yscrollcommand,
##        self.mwu_listbox = myListBox( self.master_app.all_mwu_root, [], 'mwu_viewer', lambda e : self.mwu_listbox.item_select_handler )
        self.rel_listbox = myListBox( self.master_app.all_rel_root, [], 'relation_viewer', lambda e : self.rel_selection_handler( e ) )
        self.refresh()
        #Button( master=self.master_app.all_mwu_root, text='Cancel', command=self.master_app.show_mwu_cancel_handler).pack(side='left')
        self.master_app.all_rel_root.all_rel_menu = tki.Menu( self.master_app.all_rel_root )
        self.master_app.all_rel_root.config( menu=self.master_app.all_rel_root.all_rel_menu )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Cancel', command=self.__del__ )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Refresh', command=self.refresh )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Show All', command=self.show_all_rels_handler )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Clear View', command=self.clear_view )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Set Src. Bg', command = self.set_src_bgcolor )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Set Src. Fg', command = self.set_src_fgcolor )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Set trgt. Bg', command = self.set_trgt_bgcolor )
        self.master_app.all_rel_root.all_rel_menu.add_command( label='Set trgt. Fg', command = self.set_trgt_fgcolor )
        self.master_app.all_rel_root.all_rels_on_display = True
        #----- popup menu for rels ---
        self.popup_menu = tki.Menu( self.rel_listbox, tearoff=0 )
        self.popup_menu.add_command( label='Show', command=self.rel_show_handler )
        self.popup_menu.add_command( label='Hide', command=self.rel_hide_handler  )
        self.popup_menu.add_command( label='Select', command=self.rel_select_handler )
        self.popup_menu.add_command( label='Done', command=self.rel_done_handler )
        self.popup_menu.add_command( label='Delete', command=self.rel_delete_handler  )
        self.draw()

    def set_src_bgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.src_bgcolor = hexstr

    def set_src_fgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.src_fgcolor = hexstr

    def set_trgt_bgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.trgt_bgcolor = hexstr

    def set_trgt_fgcolor( self ):
        ( (rv, bv, gv), hexstr ) = askcolor()
        self.trgt_fgcolor = hexstr
        
    def draw( self ):
        all_rel_repr = []
        n = 0
        self.all_rels_listbox_indices = {}
        for k in self.master_app.all_rels.keys():
            self.all_rels_listbox_indices[ n ] = k
            n += 1
            r = self.master_app.all_rels[ k ]
            curr_rel_repr = self.master_app.make_listbox_rel_repr( r )
            all_rel_repr.append( curr_rel_repr )                                                                                                                                            
        self.rel_listbox.delete( 0, tki.END )
        for i in all_rel_repr:
            self.rel_listbox.insert_item( all_rel_repr.index(i), i )
        self.master_app.all_rel_root.lift()

    def rel_selection_handler( self, e = None ):
##        print( 'DEBUG rel selection handler with event e: {0} at x_root={1} and y_root={2} and x={3} and y={4}'.format( e, e.x_root, e.y_root, e.x, e.y ))
        assert( e is not None )
        if( len(self.master_app.all_rels) > 0 ):
            self.popup_menu.post( e.x_root, e.y_root )

    def show_all_rels_handler( self, e = None):
        for i in range( 0, len( self.master_app.all_rels )):
            r = self.master_app.all_rels[ self.all_rels_listbox_indices[ i ]]
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( r.src ), bgcol=self.src_bgcolor, fgcol=self.src_fgcolor )
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( r.trgt ), bgcol=self.trgt_bgcolor, fgcol=self.trgt_fgcolor )                         
   
    def rel_show_handler( self, e = None ):
        items = map( int, self.rel_listbox.list.curselection() )
        for i in items:
            r = self.master_app.all_rels[ self.all_rels_listbox_indices[ i ]]
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( r.src ), bgcol=self.src_bgcolor, fgcol=self.src_fgcolor )
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( r.trgt ), bgcol=self.trgt_bgcolor, fgcol=self.trgt_fgcolor )

    def rel_hide_handler( self, e = None ):
        items = map( int, self.rel_listbox.list.curselection() )
        for i in items:
            r = self.master_app.all_rels[ self.all_rels_listbox_indices[ i ]]
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.src ))
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.trgt ))                           
                                           
    def rel_select_handler( self, e = None ):
        items = map( int, self.rel_listbox.list.curselection() )
        rellst= []
        for i in items:
            rel_nm_and_repr = ( self.all_rels_listbox_indices[ i ], self.rel_listbox.list.get( i ) )
            rellst.append( rel_nm_and_repr )
        self.master_app.selected_rel_lst = rellst
        self.__del__()

    def rel_done_handler( self, e = None ):
        dummy = None

    def rel_delete_handler( self, e = None ):
        items = map( int, self.rel_listbox.list.curselection() )
        for i in items:
            r = self.master_app.all_rels[ self.all_rels_listbox_indices[ i ]]
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.src ))
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.trgt )) 
            self.master_app.all_spans.remove( r.src )
            self.master_app.all_spans.remove( r.trgt )           
            self.master_app.all_rels.pop( self.all_rels_listbox_indices[ i ] )
            self.rel_listbox.delete( i )
        self.refresh()
        if( self.master_app.mwu_vwr is not None ):
            self.master_app.mwu_vwr.refresh()

    def run( self ):
        self.master_app.all_rel_root.mainloop()

    def __del__( self ):
        if( self.master_app.all_rel_root is not None ):
            self.master_app.all_rel_root.quit()
            self.master_app.all_rel_root.destroy()
            self.master_app.all_rel_root = None
            self.master_app.rel_vwr = None

    def refresh( self ):
##        print( '=== refresh rel viewer ========' )
        # this will provoke the death of this instance and the creation of a new instance of this class through a call to a handler of the master app.
        #self.master_app.show_mwu_cancel_handler()
        #self.master_app.mwu_vwr = self.master_app.mwu_handler()
        self.draw()
        self.lift()
        self.master_app.root.update_idletasks()

    def lift( self ):
        self.master_app.all_rel_root.lift()
 
    def clear_view( self ):
        for k in self.master_app.all_spans.get_all_keys():
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( k ))
            
#===== end of relation_viewer class ==============

class kstruct_viewer( object ):

    def __init__( self, construkt_app, x=None, y=None ):
        self.curr_file = None
        self.master_app = construkt_app
        self.kstruct_vwr_root = tki.Toplevel()
        self.kstruct_vwr_root.title( 'construction viewer' )
        self.kstruct_vwr_root.protocol( "WM_DELETE_WINDOW", self.__del__ )
        scrn_w = self.master_app.root.winfo_screenwidth()
        width = scrn_w/3
        if( x is None ):
            x = (scrn_w/3) - (width/3)
        scrn_h = self.master_app.root.winfo_screenheight()
        height = scrn_w/3
        if( y is None ):
            y = (scrn_h/3) - (height/3)
        self.kstruct_vwr_root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        self.src_fgcolor = self.master_app.fg_src_color
        self.src_bgcolor = self.master_app.bg_src_color
        self.trgt_fgcolor = self.master_app.fg_trgt_color
        self.trgt_bgcolor = self.master_app.bg_trgt_color 
        #------- top bar menu -----
        self.kstruct_vwr_done_cancel_menu = tki.Menu( self.kstruct_vwr_root )
        self.kstruct_vwr_root.config( menu=self.kstruct_vwr_done_cancel_menu  )
        self.kstruct_vwr_done_cancel_menu.add_command( label='New Construction', command = self.kstruct_vwr_new_kstruct_handler )
        self.kstruct_vwr_done_cancel_menu.add_command( label='Add Relation', command = self.rel_add_to_kstruct_handler )
        self.kstruct_vwr_done_cancel_menu.add_command( label='Delete All Constructions', command = self.kstruct_vwr_delete_all_kstructs_handler )
        self.kstruct_vwr_done_cancel_menu.add_command( label='Cancel', command = self.kstruct_vwr_cancel_handler )
        #-----------------
        self.kstruct_name_scrolled_labeled_input_text_frame = tki.Frame( self.kstruct_vwr_root )
        self.kstruct_name_scrolled_labeled_input_text_frame.pack( fill='x', expand=False, side='top')
        self.kstruct_name_scrolled_labeled_label = Label( self.kstruct_name_scrolled_labeled_input_text_frame,
                                                          text='Construction Label' )
        self.kstruct_name_scrolled_labeled_label.pack( side='left', fill='x', expand=False )
        self.construkt_name_var = StringVar(  master=self.kstruct_name_scrolled_labeled_input_text_frame )
        self.construkt_name_var.set( '' ) # null string value is tested when the popup is activated to differentiate between new and edit existing construction.
        self.kstruct_name_scrolled_input_text_frame = tki.Frame( self.kstruct_name_scrolled_labeled_input_text_frame )
        self.kstruct_name_scrolled_input_text_frame.pack( fill='x', expand=True, side='right')
##        self.kstruct_vwr_label_input_hscrollbar = Scrollbar( self.kstruct_name_scrolled_input_text_frame,
##                                                             orient=tki.HORIZONTAL)
        self.kstruct_name_scrolled_labeled_input = Entry( master=self.kstruct_name_scrolled_input_text_frame,
                                                          textvariable = self.construkt_name_var )
##                                                          , xscrollcommand= self.kstruct_vwr_label_input_hscrollbar.set )
        self.kstruct_name_scrolled_labeled_input.pack( side='top', fill='x', expand=True )
##        self.kstruct_vwr_label_input_hscrollbar.pack( side='bottom', fill='x', expand=True )
        #----intermediary labels-----------
        self.kstruct_intermediary_labels_frame = tki.Frame( self.kstruct_vwr_root )
        self.kstruct_intermediary_labels_frame.pack( side='top', fill='x', expand=False)
        self.kstruct_all_construction_label = Label( self.kstruct_intermediary_labels_frame,
                                                          text='Construction' )
        self.kstruct_all_construction_label.pack( side='left', fill='x', expand=True )
        #----
        self.kstruct_relations_label_prefix = 'Relations of '
        self.kstruct_relations_label = Label( self.kstruct_intermediary_labels_frame )
        # Important for having the Label widget to update when the variable change value, it needs to have a master assigned at creation!
        self.kstruct_relations_label_prefix_var = StringVar(  master=self.kstruct_intermediary_labels_frame ) #creation of a variable associated to the label text.
        self.kstruct_relations_label_prefix_var.set( self.kstruct_relations_label_prefix )
        self.kstruct_relations_label.config( textvariable = self.kstruct_relations_label_prefix_var )
        self.kstruct_relations_label.pack( side='right', fill='x', expand=True )
        #--- view list frame -----
        self.kstruct_two_list_frame = tki.Frame( self.kstruct_vwr_root )
        self.kstruct_two_list_frame.pack( side='bottom', fill='both', expand=True )
        #------ view of the list of all the constructions names -----
        self.kstruct_vwr_kstruct_listbox = myListBox( root=self.kstruct_two_list_frame,
                                                items=[],
                                                id='kstruct_vwr_relation_lst',
                                                item_select_handler=self.kstruct_vwr_kstruct_lst_handler,
                                                smode = tki.SINGLE )
        self.kstruct_vwr_kstruct_listbox.pack( side='left', fill='both', expand=True )
        #----- view of the relation list of the currently selected construction name -----
        self.kstruct_vwr_rel_listbox = myListBox( root=self.kstruct_two_list_frame,
                                                items=[],
                                                id='kstruct_vwr_kstruct_lst',
                                                item_select_handler= self.kstruct_vwr_relation_lst_handler,
                                                smode = tki.EXTENDED )
        self.kstruct_vwr_rel_listbox .pack( side='right', fill='both', expand=True )
        #-----------
        self.master_app.kstruct_vwr_on_display = True
        self.kstruct_vwr_rel_listbox_indices = {}
        self.kstruct_vwr_selected_rels = []
        self.kstruct_vwr_kstruct_listbox_indices = {}
        self.curr_selected_kstruct_nm = ''  # One cannot select more than one construction at a time.
        #-------- kstructs popup
        self.kstructs_popup_menu = tki.Menu( self.kstruct_vwr_kstruct_listbox, tearoff=0 )
        self.kstructs_popup_menu.add_command( label='Show', command=self.kstruct_vwr_kstructs_show_handler )
        self.kstructs_popup_menu.add_command( label='Hide', command=self.kstruct_vwr_kstructs_hide_handler  )
        self.kstructs_popup_menu.add_command( label='Done', command=self.kstruct_vwr_kstructs_done_handler )
        self.kstructs_popup_menu.add_command( label='Delete', command=self.kstruct_vwr_kstructs_delete_handler  )
        #-------- rels popup
        self.rels_popup_menu = tki.Menu( self.kstruct_vwr_rel_listbox, tearoff=0 )
        self.rels_popup_menu.add_command( label='Show', command=self.kstruct_vwr_rels_show_handler )
        self.rels_popup_menu.add_command( label='Hide', command=self.kstruct_vwr_rels_hide_handler  )
        self.rels_popup_menu.add_command( label='Done', command=self.kstruct_vwr_rels_done_handler )
        self.rels_popup_menu.add_command( label='Remove', command=self.kstruct_vwr_rels_remove_handler  )
        #------
        self.refresh_handler()
        
    def run( self ):
        self.kstruct_vwr_root.mainloop()

    def __del__( self ):
        if( self.master_app.kstruct_vwr is not None ):
            self.kstruct_vwr_root.update_idletasks()
            self.kstruct_vwr_root.quit()
            self.kstruct_vwr_root.destroy()
            self.kstruct_vwr_root = None
            self.master_app.kstruct_vwr = None

    def kstruct_vwr_cancel_handler( self, e = None ):
##        print( 'kstruct_vwr_cancel_handler' )
        self.__del__()

    def kstruct_vwr_delete_all_kstructs_handler( self, e = None ):
        self.master_app.all_kstructs = {}
        self.curr_selected_kstruct_nm = ''
        self.redraw() 
            
    def kstruct_vwr_delete_kstruct_handler( self, e = None ):
        items = list(map( int, self.kstruct_vwr_kstruct_listbox.list.curselection() ))
        assert( (len( items ) == 0) or (len( items ) == 1) )
        if( len( items ) == 1 ): 
            self.kstruct_vwr_kstructs_hide_handler()
            knm = self.kstruct_vwr_kstruct_listbox_indices[ items[ 0 ]]
            self.curr_selected_kstruct_nm = knm
            if( len( self.kstruct_vwr_kstruct_listbox_indices ) > 1 ): # we have at least two constructions, so we can put the focus on the last one
                if( items[ 0 ] == 0 ):
                   self.kstruct_vwr_kstruct_listbox.generate_select_event( 1 )
                else:
                   self.kstruct_vwr_kstruct_listbox.generate_select_event( items[ 0 ]-1 ) 
            self.kstruct_vwr_kstruct_listbox_indices.pop( items[ 0 ] )
            self.master_app.all_kstructs.pop( knm )
        self.redraw()

    def kstruct_vwr_new_kstruct_handler( self ):
        # a construction is always created first without any relation.
        # Relation are added to the construction afterwards.
        self.new_knm = self.construkt_name_var.get()
        if( (self.new_knm == '') or (self.new_knm in self.kstruct_vwr_kstruct_listbox_indices.values())): # if the input name is empty or already exists we create a new one
            self.new_knm = self.master_app.name_mgr.create_name( ConstruKT.CONSTRU_TYP ) 
        self.curr_selected_kstruct_nm = self.new_knm
        self.construkt_name_var.set( self.curr_selected_kstruct_nm )
        self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ] = construction( nm = self.curr_selected_kstruct_nm, rel_lst = [] )
        self.master_app.last_kstruct = self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ]
        #----- update the construction name widget and the construction listbox
        self.kstruct_relations_label_prefix_var.set( self.kstruct_relations_label_prefix + self.curr_selected_kstruct_nm )
        new_i = len( self.kstruct_vwr_kstruct_listbox_indices )
        self.kstruct_vwr_kstruct_listbox_indices[ new_i ] = self.curr_selected_kstruct_nm
        self.kstruct_vwr_kstruct_listbox.insert_item( new_i, self.curr_selected_kstruct_nm )
        self.kstruct_vwr_kstruct_listbox.select_set( new_i )
        self.kstruct_vwr_kstruct_listbox.activate( new_i )
        self.kstruct_vwr_kstruct_listbox.index( new_i )
        self.kstruct_vwr_rel_listbox_indices = { }
        self.kstruct_vwr_rel_listbox.delete( 0, tki.END )
        self.master_app.selected_rel_lst = []
        self.kstruct_vwr_kstruct_listbox.generate_select_event( new_i )
        
    def rel_add_to_kstruct_handler( self ):
        if( self.curr_selected_kstruct_nm is not None ):
            # Note: one can only add relations to a pre-existing construction
            self.master_app.rel_handler()
            n = len( self.kstruct_vwr_rel_listbox_indices )
            repr_lst = []
            for (rel_nm, rel_repr ) in self.master_app.selected_rel_lst:
                if( rel_nm not in self.kstruct_vwr_rel_listbox_indices.values() ):
                    self.kstruct_vwr_rel_listbox_indices[ n ] = rel_nm
                    n += 1
                    repr_lst.append( rel_repr )
##                    print( 'DEBUG curr_selected_kstruct_nm = {0}'.format( self.curr_selected_kstruct_nm ))
                    self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ].rels.append( rel_nm )
            self.master_app.selected_rel_lst = []
            i = 0
            for r in repr_lst:
                self.kstruct_vwr_rel_listbox.insert_item( i, r )
                i += 1
            self.kstruct_vwr_root.lift()

    def redraw( self ):
        #------- konstructs listbox redrawing
        self.kstruct_vwr_kstruct_listbox.delete( 0, tki.END )
        self.kstruct_vwr_rel_listbox.delete( 0, tki.END )
        k = 0
        krepr_lst = []
        self.kstruct_vwr_kstruct_listbox.delete( 0, tki.END )
        for knm in self.master_app.all_kstructs.keys():
            self.kstruct_vwr_kstruct_listbox.insert_item( k, knm )
            self.kstruct_vwr_kstruct_listbox_indices[ k ] = knm
            k += 1
            self.master_app.last_kstruct = self.master_app.all_kstructs[ knm ]
            self.curr_selected_kstruct_nm = knm
            i = 0
            repr_lst = []
            for rnm in self.master_app.all_kstructs[ knm ].rels:
                curr_repr = self.master_app.make_listbox_rel_repr( self.master_app.all_rels[ rnm ])
                repr_lst.append( curr_repr )
                self.kstruct_vwr_rel_listbox.insert_item( i, self.master_app.make_listbox_rel_repr( self.master_app.all_rels[ rnm ]))
                self.kstruct_vwr_rel_listbox_indices[ i ] = rnm
                i += 1
        self.construkt_name_var.set( '' )
        self.aux_ilst = list( self.kstruct_vwr_kstruct_listbox_indices.values())
        if( self.curr_selected_kstruct_nm != '' ):
            if( self.curr_selected_kstruct_nm in self.aux_ilst ):
                self.kstruct_vwr_kstruct_listbox.generate_select_event( self.aux_ilst.index( self.curr_selected_kstruct_nm ))
        else:
            if( self.aux_ilst != [] ):
                self.kstruct_vwr_kstruct_listbox.generate_select_event( 0 )
        self.kstruct_vwr_kstruct_listbox.root.update_idletasks()

    def refresh_handler( self ):
        self.redraw()
        self.kstruct_vwr_root.update_idletasks()

    def kstruct_vwr_kstruct_lst_handler( self, e = None ):
        self.items = list( map( int, self.kstruct_vwr_kstruct_listbox.list.curselection() ))
        n = 0
        for i in self.items:
            n += 1
        assert( (n == 0) or (n == 1) )
        if( n != 0 ):
                self.curr_selected_kstruct_nm = self.kstruct_vwr_kstruct_listbox_indices[ self.items[ 0 ] ] # the name of the selecte construction
                self.kstruct_relations_label_prefix_var.set( self.curr_selected_kstruct_nm )
                curr_repr = ''
                repr_lst = []
                for rnm in self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ].rels:
                        curr_repr = self.master_app.make_listbox_rel_repr( self.master_app.all_rels[ rnm ] )
                        repr_lst.append( curr_repr )
                self.kstruct_vwr_rel_listbox.delete( 0, tki.END )
                k = 0
                for k in range( 0, len( repr_lst)):
                    self.kstruct_vwr_rel_listbox.insert_item( k, repr_lst[ k ] )
                self.kstructs_popup_menu.post( e.x_root, e.y_root )

    # -----------kstructs popup handlers

    def kstruct_vwr_kstructs_show_handler ( self, e = None ):
        self.items = list(map( int, self.kstruct_vwr_kstruct_listbox.list.curselection()))
        assert( (len( self.items) == 0) or (len( self.items) == 1))
        for i in self.items:
            k = self.master_app.all_kstructs[ self.kstruct_vwr_kstruct_listbox_indices[ i ]]
            for rnm in k.rels:
                self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].src ),
                                  bgcol=self.src_bgcolor,
                                  fgcol=self.src_fgcolor )
                self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].trgt ),
                                  bgcol=self.trgt_bgcolor,
                                  fgcol=self.trgt_fgcolor )                                 

    def kstruct_vwr_kstructs_hide_handler ( self, e = None ):
        self.items = list(map( int, self.kstruct_vwr_kstruct_listbox.list.curselection()))
        assert( (len( self.items) == 0) or (len( self.items) == 1))
        for i in self.items:
            k = self.master_app.all_kstructs[ self.kstruct_vwr_kstruct_listbox_indices[ i ]]
            for rnm in k.rels:
                r = self.master_app.all_rels[ rnm ]
                self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.src  ))
                self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( r.trgt ))                             
        
    def kstruct_vwr_kstructs_done_handler ( self, e = None ):
        # update of self.curr_selected_kstruct_nm is taken care of in kstruct_vwr_kstruct_lst_handler( self, e = None )
        self.dummy = None

    def kstruct_vwr_kstructs_delete_handler ( self, e = None ):
        self.kstruct_vwr_kstructs_hide_handler()
        self.kstruct_vwr_delete_kstruct_handler()
        
    #------------------------    

    def kstruct_vwr_relation_lst_handler( self, e = None ):
        assert( e is not None )
        if( len( self.kstruct_vwr_rel_listbox_indices ) > 0 ):
            self.rels_popup_menu.post( e.x_root, e.y_root )
            
    # -----------rels popup handlers

    def kstruct_vwr_rels_show_handler ( self, e = None ):
        self.relitems = map( int, self.kstruct_vwr_rel_listbox.list.curselection() )
        for i in self.relitems:
            rnm = self.kstruct_vwr_rel_listbox_indices[ i ]
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].src ),
                                                                        bgcol=self.src_bgcolor,
                                                                        fgcol=self.src_fgcolor )                                 
            self.master_app.color_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].trgt ),
                                         bgcol=self.trgt_bgcolor,
                                         fgcol=self.trgt_fgcolor )


    def kstruct_vwr_rels_hide_handler ( self, e = None ):
        self.relitems = map( int, self.kstruct_vwr_rel_listbox.list.curselection() )
        for i in self.relitems:
            rnm = self.kstruct_vwr_rel_listbox_indices[ i ]
            r = self.master_app.all_rels[ rnm ]
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].src ))
            self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].trgt ))                            

    def kstruct_vwr_rels_done_handler ( self, e = None ):
        self.dummy = None

    def kstruct_vwr_rels_remove_handler ( self, e = None ):
        if( self.curr_selected_kstruct_nm != '' ):
            self.relitems = map( int, self.kstruct_vwr_rel_listbox.list.curselection() )
            for i in self.relitems:
                rnm = self.kstruct_vwr_rel_listbox_indices[ i ]
                # hide if in case rel is displayed
                r = self.master_app.all_rels[ rnm ]
                self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].src ))
                self.master_app.hide_mspan( wnts_lst = self.master_app.all_spans.get( self.master_app.all_rels[ rnm ].trgt ))                             
                self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ].rels.remove( rnm )
            for i in self.relitems:
                del self.kstruct_vwr_rel_listbox_indices[ i ]
            self.master_app.selected_rel_lst = []
        self.refresh_handler()
        
    #-----end of rels popup menu handlers

    def kstruct_viewer_cancel_handler( self, e = None ):
        self.__del__()
  
#---- end of kstruct class ---------------------------------------------------------------------------------

class ConstruKT(object):

    def __init__(self, doc=None, text=None, x=None, y=None, config_path = None ):
        self.config = {} # a dictionary holding attribute value associations for configuring some annotation application, e.g. the treetagger: { 'TREEAGGER_DIR':'/people/koroleva/Desktop/src/TreeTagger'}
        if( config_path is not None ):
            assert(  type( config_path is str ) and os.path.isfile( config_path ) )
            f = open( config_path, 'r' )
            self.config = eval( f.read() )
            f.close()
        assert( (doc is None) or (text is None) )
        # given to namespace, the list of various type names used to build object names (unique identifiers)
        ConstruKT.SPAN_TYP = 'SPAN'
        ConstruKT.MWU_TYP = 'MWU'
        ConstruKT.SRC_TYP = 'SRC'
        ConstruKT.TRGT_TYP = 'TRGT'
        ConstruKT.REL_TYP = 'REL'
        ConstruKT.CONSTRU_TYP = 'CONSTRU'
        ConstruKT.ALL_TYPS =  [ ConstruKT.SPAN_TYP, ConstruKT.MWU_TYP, ConstruKT.SRC_TYP, ConstruKT.TRGT_TYP, ConstruKT.REL_TYP, ConstruKT.CONSTRU_TYP  ] 
        self.name_mgr = namespace( ConstruKT.ALL_TYPS )
        #--------
        #   graphic preferences
        self.default_bg_color = 'white'
        self.default_fg_color = 'black'
        self.new_mwu_bg_color = 'orange'
        self.new_mwu_fg_color = 'black'
        self.mwu_bg_color = 'yellow'
        self.mwu_fg_color = 'black'
        self.bg_new_src_color = 'white'
        self.fg_new_src_color = 'orange'  
        self.bg_new_trgt_color = '#ceeb99'  # a sort of light blueish green
        self.fg_new_trgt_color = 'black'
        self.bg_src_color = 'white'
        self.fg_src_color = 'red'           # MWU sources are represented with foreground color so they can overlap with targets
        self.bg_trgt_color = 'light green'   # MWU targets are represented with background color so they can overlap with sources
        self.fg_trgt_color = 'black'
        self.select_bg_color = 'light grey'
        self.select_fg_color = 'black'
        self.select_frame_width = 4
        #--------------------
        self.last_txt_sel_beg = None # linepos.charpos of start (first char  index) of last text selection
        self.last_txt_sel_end = None # linepos.charpos of end (first char index AFTER last char) of last text selection
        # e.g.  sel.first at 7.637  and sel.last at 7.642 for selection of 5 characters at line 7 starting at pos 637
        self.last_sel_wnts = None
        #-------- mwus management ----------
        # a list holding the name of each mwu
        self.all_spans = namelistmap()
        # to maintain consistency between mwu names and relations sources and targets when importing
        # data where mwu are unnecessarily duplicated over the same text spans with the same type
        self.mwu_alias_table = namelistmap()
        self.last_MWU_span = ''  # will hold a source multi-word span identifier in self.all_spans
        self.last_SRC_span = ''  # will hold a source multi-word span identifier in self.all_spans 
        self.last_TRGT_span = ''  # will hold a target multi-word span identifier in self.all_span
        self.last_MWU_type_var = None
        # a list associating to each mwu name its type (NOTE: the namelistmap enables
        self.last_rel_nm = None
        # dictionary holding the name of each relation
        self.all_rels = { }
        # dictionary holding the name of each construction
        self.all_kstructs = { }
        #------------------------
        # data is text content
        if( doc is not None ):
            self.data = doc.ctnt
        else:
            if( text is not None ):
                self.data = text
            else:
                self.data = ''
        self.doc = doc
        # a list holding pairs made of the first charoffset position of the first character of each line and of the considered line length
        self.lc_coords_map = [] 
        self.old_data = ''
        #------------------------
        self.curr_span_wnts_lst = []
        self.curr_file = None
        self.root = tki.Tk()
        self.root.title( 'ConstruKT a Constructions Kit of Tools' )
        if( x is None ):
            scrn_w = self.root.winfo_screenwidth()
            width = scrn_w/2
            x = (scrn_w/2) - (width/2)
        if( y is None ):
            scrn_h = self.root.winfo_screenheight()
            height = scrn_w/2
            y = (scrn_h/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        # width in characters and height in lines
        # STANDARD OPTIONS
        ##        background, borderwidth, cursor,
        ##        exportselection, font, foreground,
        ##        highlightbackground, highlightcolor,
        ##        highlightthickness, insertbackground,
        ##        insertborderwidth, insertofftime,
        ##        insertontime, insertwidth, padx, pady,
        ##        relief, selectbackground,
        ##        selectborderwidth, selectforeground,
        ##        setgrid, takefocus,
        ##        xscrollcommand, yscrollcommand,
        self.textPad = ScrolledText(self.root, wrap='word', undo=True,
                                    # color of the widget frame when holding the focus
                                    # highlightcolor='orange',
                                    # color of the widget frame when not holding the focus
                                    # highlightbackground='purple',
                                    # width of the focus frame
                                    # highlightthickness=5 ,
                                    # background color for the selected text
                                    selectbackground = self.select_bg_color,
                                    # width of the border around the selected text
                                    selectborderwidth = self.select_frame_width,
                                    # forground color for the selected text
                                    selectforeground = self.select_fg_color )
        
        self.textPad.insert( 1.0, self.data )
        # ----- current selection label ------------
        self.cursellabel = Label( self.root )
        self.curselprompt = 'CURRENT SELECTION: '
        # Important for having the Label widget to update when the variable change value, it needs to have a master assigned at creation!
        self.feedback_label_text = StringVar(  master=self.root ) #creation of a variable associated to the label text.
        self.feedback_label_text.set( self.curselprompt )
        self.cursellabel.config( textvariable = self.feedback_label_text )
        self.cursellabel.pack()
        #------ SRC label -----------------------
        self.cursrclabel = Label( self.root )
        self.cursrcprompt = 'CURRENT SOURCE: '
        # Important for having the Label widget to update when the variable change value, it needs to have a master assigned at creation!
        self.feedback_label_src = StringVar(  master=self.root ) #creation of a variable associated to the label text.
        self.feedback_label_src.set( self.cursrcprompt )
        self.cursrclabel.config( textvariable = self.feedback_label_src )
        self.cursrclabel.pack()
        #------ TRGT label -----------------------
        self.curtrgtlabel = Label( self.root  )
        self.curtrgtprompt = 'CURRENT TARGET: '
        # Important for having the Label widget to update when the variable change value, it needs to have a master assigned at creation!
        self.feedback_label_trgt = StringVar(  master=self.root ) #creation of a variable associated to the label text.
        self.feedback_label_trgt.set( self.curtrgtprompt )
        self.curtrgtlabel.config( textvariable = self.feedback_label_trgt )
        self.curtrgtlabel.pack()
        #-------- menus and commands --------------
        self.textPad.pack( side=tki.LEFT, expand=True, fill='both' )
        self.textPad['font'] = ('consolas', '12')
        self.menu = tki.Menu( self.root )
        self.root.config( menu=self.menu )
        #----file menu------
        self.filemenu = tki.Menu( self.menu )
        self.menu.add_cascade( label='File', menu=self.filemenu )
        self.filemenu.add_command( label='Import Text & Annotation', command=self.import_TandA_handler )
        self.filemenu.add_command( label='Import Text Only', command=self.import_Tonly_handler )
        self.filemenu.add_command( label='Export Text & Annotation', command=self.export_TandA_handler )
        self.filemenu.add_command( label='Export Text Only',  command=self.export_Tonly_handler )
        self.filemenu.add_separator()
        self.filemenu.add_command( label='Exit',     command=self.exit_handler )
        #----- Annotations menu ---
        self.annotationmenu = tki.Menu( self.menu )
        self.menu.add_cascade( label='Annotations', menu=self.annotationmenu )
        self.annotationmenu.add_command( label='Multi-Word Units',  command=self.mwu_handler     )
        self.annotationmenu.add_command( label='Relations',  command=self.rel_handler )
        self.annotationmenu.add_command( label='Constructions',  command=self.kstruct_view_handler )
        self.annotationmenu.add_command( label='Metadata',  command=self.meta_view_handler )
##        self.annotationmenu.add_command( label='New Construction',  command=self.kstruct_edit_handler )
        self.annotationmenu.add_command( label='Clear View',  command=self.clear_view_handler )
        self.annotationmenu.add_command( label='Refresh View', command=self.refresh_view_handler )
        
        self.annotationmenu.add_separator()
        self.annotationmenu.add_command( label='Cancel', command=self.cancel_handler )
        #------ Constructions menu
##        self.kstruct_menu = tki.Menu( self.menu )
##        self.menu.add_cascade( label='Constructions', menu=self.kstruct_menu )
##        self.kstruct_menu.add_separator()
##        self.kstruct_menu.add_command( label='Cancel',     command=self.kstruct_cancel_handler )
        #----- Annotation algorithms ---
        self.algo_menu = tki.Menu( self.menu )
        self.menu.add_cascade( label='Algorithms', menu=self.algo_menu )
        self.algo_menu.add_command( label='Co-occurrences',  command=self.algo_cooccurrences_handler )
        self.algo_menu.add_separator()

        # create an Annotate object for the Construkt object
        # empty because there is no data yet
        self.Annotate = None        

        self.algo_menu.add_command( label='Find Primary Outcomes',  command=self.algo_preannotate_po_handler )
        self.algo_menu.add_command( label='Find Reported Outcomes',  command=self.algo_preannotate_rep_out_handler )
        self.algo_menu.add_command( label='Extract Registry Data',  command=self.algo_registry_data_handler )

        self.algo_menu.add_separator()

        self.algo_menu.add_command( label='Compare: Primary Outcomes (Abstract) / Primary Outcomes (Body)',  command=self.algo_compare_po_abstr_bt_handler )
        self.algo_menu.add_command( label='Compare: Primary Outcomes (Registry) / Primary Outcomes (Article)',  command=self.algo_compare_po_reg_text_handler )
        self.algo_menu.add_command( label='Compare: Primary Outcomes (Registry) / Reported Outcomes (Article)',  command=self.algo_compare_rep_reg_text_handler )
        self.algo_menu.add_command( label='Compare: Primary Outomes (Article) / Reported Outcomes (Article)',  command=self.algo_compare_po_rep_handler )

        self.algo_menu.add_separator()

        self.algo_menu.add_command( label='Find Statistical Measures',  command=self.algo_preannotate_stat_handler )
        self.algo_menu.add_command( label='Find Significance Levels for Outcomes',  command=self.algo_signif_rels_handler )

        self.algo_menu.add_separator()

        self.algo_menu.add_command( label='Find Similarity Statements',  command=self.algo_find_sim_handler )
        self.algo_menu.add_command( label='Annotate Non-inferiority/Equivalence Design',  command=self.algo_preannotate_noninf_handler )

        self.algo_menu.add_separator()

        self.algo_menu.add_command( label='Find Within-Group Comparisons',  command=self.algo_find_wgc_handler )
        self.algo_menu.add_command( label='Find Recommendations',  command=self.algo_find_rec_handler )
        self.algo_menu.add_command( label='Find Hedge',  command=self.algo_find_hedge_handler )
        self.algo_menu.add_command( label='Annotate Positive Evaluations',  command=self.algo_preannotate_pos_eval_handler )

        self.algo_menu.add_separator()

        self.algo_menu.add_command( label='Text Structure',  command=self.algo_text_structure_handler )
        self.algo_menu.add_command( label='Abstract Structure',  command=self.algo_abstract_structure_handler )
        self.algo_menu.add_command( label='Abbreviations',  command=self.algo_abbreviations_handler )

        self.algo_menu.add_separator()
        self.algo_menu.add_command( label='Generate report',     command=self.generate_report_handler )
        self.algo_menu.add_command( label='Cancel',     command=self.algo_cancel_handler )
        #----- Help menu ---
        self.helpmenu = tki.Menu( self.menu )
        self.menu.add_cascade( label='Help', menu=self.helpmenu )
        self.helpmenu.add_command( label='A simple linguistic construction editor...', command=self.about_handler )
        # -----------------
        # popup menu triggered by the text 'sel' event from the ScrolledText widget
        self.popup_menu = tki.Menu( tearoff=0 )
        self.popup_menu.add_command( label='Add Text Span', command=self.add_text_span_handler )
        self.popup_menu.add_command( label='Last Text Span', command=self.last_text_span_handler )
        self.popup_menu.add_command( label='Unmark Text Span', command=self.unmark_text_span_handler )
        self.popup_menu.add_command( label='Done', command=self.done_select_handler )
        #-------------- warnings and errors popups -----
        self.overlap_select_menu = tki.Menu( tearoff=0 )

        # ------ specific events bindings

##        print( 'DEBUG binding event order: widget id, widget class, root window, all event at application level' )
##        textPad_bindings_order = self.textPad.bindtags()
##        print( 'DEBUG main text pad binding events order is: {0}'.format( textPad_bindings_order  ))

        self.textPad.tag_bind( 'sel', '<1>', lambda e: self.text_sel_handler( e ))
        self.text_sel_on = True
        
##        # reorder bindings so that the callback() for select event is executed before the callback() for single click
##        # since in ScrolledTextPad a select event is triggered when two clicks follow whithin a given time limit (double click)
##        # so we put the handler of the widget class before the handler of the widget itself as follows:
##        self.textPad.bindtags((textPad_bindings_order[1], textPad_bindings_order[0], textPad_bindings_order[2], textPad_bindings_order[3]))
        
        self.root.bind( '<1>', lambda e: self.annotation_win_click_handler( e.x_root, e.y_root, e.num ) )
        
        self.overlap_select_menu.add_command( label='Cancel', command=self.cancel_handler )

        # root windows for popup widgets and secondary views
        self.last_text_span_popup_root = None
        self.disambig_root = None
        self.create_rel_popup_root = None
        self.all_mwu_root = None
        self.all_rel_root = None
        self.kstruct_vwr_root = None
        self.all_mwus_on_display = False
        self.all_rels_on_display = False
        self.kstruct_vwr_on_display = False
##        self.kstruct_editor_on_display = False
        self.mwu_vwr = None
        self.rel_vwr = None
        self.kstruct_vwr = None
        self.meta_vwr = None
##        self.kstruct_editor = None
        self.selected_rel_lst = [] # list made of pairs (rel_name, rel_list_box_text_representation).
        self.old_all_kstructs = { }
        self.all_kstructs = { }

        # to handle closing event from the window manager (e.g. using the window frame decoration close button)
        self.root.protocol( "WM_DELETE_WINDOW", self.exit_handler )
        
    #---- end of __init__() --------------------------------------------------------------------
    
    def __del__( self ):
        self.root = None

    # ---- utils ---

    def coordinates( self, textPad_pos ):
        l = textPad_pos.split( '.' )
        return( l[0], l[1] )

    def make_lc_coord_map( self, txt ):   
        pos = 0
        lnbr = 0 
        self.lc_coords_map = [] 
        for l in txt.split( '\n' ):
            lsz = len( l )
            self.lc_coords_map.append( (pos, lsz ) )
            pos += lsz + 1  # +1 is for the newline char in Unix, but if handling windows CR-LF it needs to be 2!
            lnbr += 1

    def text_widget_line_idx( self, char_offset ):
        i = 0
        for (lstart, lsz) in self.lc_coords_map:
            if( (char_offset >= lstart ) and (char_offset <= lstart+lsz)):
                return( str(i+1) ) #+1 because first line index of Tkinter textPad widget is 1.
            i += 1
        
    def text_widget_col_idx( self, char_offset ):
        for (lstart, lsz) in self.lc_coords_map:
            if( (char_offset >= lstart ) and (char_offset <= lstart+lsz)):
                return( str( char_offset - lstart) )

    def set_data( self, txt ):
        self.data = txt
        self.make_lc_coord_map( txt )
        
    #---- starts the application main event loop

    def run( self ):
        # make the text not editable
        self.textPad.config( state='disabled' )
        self.root.mainloop()

    def destroy_auxiliary_root_windows( self ):
        # transient auxiliary windows (popups etc.)
        if( self.last_text_span_popup_root is not None ): self.last_text_span_popup_root.destroy(); self.last_text_span_popup_root = None
        if( self.disambig_root is not None ):             self.disambig_root.destroy();             self.disambig_root = None
        if( self.create_rel_popup_root is not None ):     self.create_rel_popup_root.destroy();     self.create_rel_popup_root = None
        # auxiliary window which have an arbitray life parallel to the main window
        if( self.all_mwus_on_display ): self.show_mwu_cancel_handler()
        if( self.kstruct_vwr is not None ): self.kstruct_vwr.__del__()

    def self_textPad_delete_window_handler( self ):
        self.textPad = None

    #---annotation algorithms -----------

    def import_mwu_list( self, txt,  mwul ):
        self.make_lc_coord_map( txt )
        wnts_lst = []
        for m in mwul:
            for sp in m.txtspans:
                w_beg = self.text_widget_line_idx(  sp[0] ) + '.' + self.text_widget_col_idx(  sp[0] )
                w_end = self.text_widget_line_idx(  sp[1] ) + '.' + self.text_widget_col_idx(  sp[1] )
                
                w = wnts( self.name_mgr.create_name( ConstruKT.SPAN_TYP ), w_beg, w_end, text_widget = self.textPad )

                w.show() # creation of the widget text spans making the multi-word unit
                wnts_lst.append( w )
                
            if( self.name_mgr.which_name_type( m.name, ConstruKT.MWU_TYP )):
                 self.create_mwu_span( mltspan_nm = self.name_mgr.create_name( ConstruKT.MWU_TYP ), curr_widget_mwu_span_lst = wnts_lst, typ = m.typ )
            else:
                self.name_mgr.add_name( m.name, ConstruKT.MWU_TYP )
                self.create_mwu_span( mltspan_nm = m.name, curr_widget_mwu_span_lst = wnts_lst, typ = m.typ )
            wnts_lst = []
            
        if( self.mwu_vwr is not None ):
            self.mwu_vwr.draw()
        self.refresh_view_handler()

    def import_rel_list( self, txt, rellst ):
        for r in rellst:
            k = self.mwu_alias_table.get_key_for( r.src )
            if( k is not None  ):
                self.new_src = k
            else:
                self.new_src = r.src
            assert( self.all_spans.get( self.new_src ) )
           
            k = self.mwu_alias_table.get_key_for( r.trgt )
            if( k is not None  ):
                self.new_trgt = k
            else:
                self.new_trgt = r.trgt
            assert( self.all_spans.get( self.new_trgt ) )
            
            if( self.name_mgr.which_name_type( r.name, ConstruKT.REL_TYP )):
                 self.create_relation(  n = r.name , s = self.new_src, t = self.new_trgt )
            else:
                self.name_mgr.add_name( r.name, ConstruKT.REL_TYP )
                self.create_relation(  n = r.name, s = self.new_src, t = self.new_trgt)
        if( self.rel_vwr is not None ):
            self.rel_vwr.draw()
        self.refresh_view_handler()

    def import_metadata( self, metadata ):
        self.doc.meta = self.doc.meta + '\n' + metadata
        self.refresh_view_handler()

    def import_kstruct_list( self, txt, kstruct_lst ):
         for k in kstruct_lst:
            if( self.name_mgr.which_name_type( k.name, ConstruKT.CONSTRU_TYP )):
                new_nm = self.master_app.name_mgr.create_name( ConstruKT.CONSTRU.TYP )
                self.master_app.all_kstructs[ new_nm ] = construction( nm = new_nm, rel_lst = k.rels )
            else:
                self.master_app.name_mgr.add_name( k.name, ConstruKT.CONSTRU_TYP )
                self.master_app.all_kstructs[ self.curr_selected_kstruct_nm ] = construction( nm = k.name, rel_lst = k.rels)

    def algo_cooccurrences_handler( self ):
        cooc = SFRel()
        d = cooc.token_same_form_rels_text( self.data )
        spans = []
        self.import_mwu_list( self.data, d.mwus )
        self.import_rel_list( self.data, d.rels )


    def algo_find_sim_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'find_sim_synt', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )

		
    def algo_find_wgc_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'find_wgc_synt', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_find_rec_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'find_rec', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )		


    def algo_find_hedge_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'find_hedge_synt', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        

    def algo_preannotate_po_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'preannot_po_biobert', preann_parser = 'bert', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_preannotate_rep_out_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'preannot_rep_scibert', preann_parser = 'bert', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_preannotate_stat_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'preannot_stat', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_preannotate_noninf_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'preannot_noninf', allow_intersection = False )
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_preannotate_pos_eval_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        mwus_preannot = self.Annotate.preannot_to_mwu( preannot_function = 'find_eval_synt', allow_intersection = True )

        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def algo_compare_po_abstr_bt_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.compare_outcomes_abstract_to_body()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )


    def algo_compare_po_reg_text_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )
            
        self.Annotate.compare_po_text_to_registry()
        
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )


    def algo_compare_rep_reg_text_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )
            
        self.Annotate.compare_rep_text_to_registry()
        
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )


    def algo_compare_po_rep_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.compare_po_to_reported()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )


    def algo_signif_rels_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.signif_rels()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )

    def algo_text_structure_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.detect_text_structure()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )

    def algo_abstract_structure_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.detect_abstract_structure()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )

    def algo_registry_data_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.find_registry_data()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )
        self.import_metadata( self.Annotate.doc.meta )


    def algo_abbreviations_handler( self ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        self.Annotate.find_abbreviations()
                
        self.import_mwu_list( self.data, self.Annotate.doc.mwus )
        self.import_rel_list( self.data, self.Annotate.doc.rels )


    def generate_report_handler( self, path = os.path.join(os.path.expanduser('~'), "Desktop/report")): # + os.path.basename(self.curr_file)) ):
        if self.Annotate == None:
            self.Annotate = Annotate( data = self.data, config_path = my_config_path )

        report = self.Annotate.generate_report()
        res_file = codecs.open(path, 'w', encoding = 'utf-8')
        res_file.write(report)
        res_file.close()        

    def algo_cancel_handler( self ):
        print( 'algo_run_cancel_handler' )

        
    #----- annotation window text selection event ------

    def annotation_win_click_handler( self, root_x, root_y, mbt ):
##        # I do not need to handle button clicks from the ScrolledTextPad window
##        # because text selection event are triggered only when a click happens inside a selected texte zone (highlighted in grey by the own widgets callbacks).
        print( 'button1 click at {0} {1} button= {2} (meaning 1, 2, 3 = (left, middle, right) 4, 5 = (scroll up, down)'.format( root_x, root_y, mbt ) )
        # by default on linux (ubuntu), ScrolledTextPad is sensitive only to button1 clicks
          
    def text_sel_handler( self, event ):
        if( self.text_sel_on ):
            txt = self.textPad.get( 'sel.first', 'sel.last' )
            self.last_txt_sel_beg = self.textPad.index( 'sel.first' )
            self.last_txt_sel_end = self.textPad.index( 'sel.last' )
            span_nm = self.name_mgr.create_name( ConstruKT.SPAN_TYP ) 
            self.last_sel_wnts = wnts( span_nm, self.last_txt_sel_beg, self.last_txt_sel_end, self.textPad )
            self.last_sel_wnts.color( bg=self.select_bg_color)
##            self.textPad.tag_config( 'sel', background=self.select_bg_color, foreground=self.select_fg_color )
            self.popup_menu.post( event.x_root, event.y_root )

    #--------- top bar menu, file menu  ---------------------------------------

    def import_TandA_handler( self ):
        file = filedialog.askopenfilename( parent=self.root, title='Select a file')
        if( (file != None) and (file != '') and (file != ()) ):
            if( self.mwu_vwr is not None ):
                self.mwu_vwr.mwu_vwr_cancel_handler()
            if( self.rel_vwr is not None ):
                self.rel_vwr.rel_vwr_cancel_handler()
            if( self.kstruct_vwr is not None ):
                self.kstruct_vwr.kstruct_vwr_cancel_handler()
            self.all_spans = namelistmap()
            self.all_rels = {}
            self.all_kstructs = {}
            with open(file, mode='r', encoding = 'utf-8') as f:
                file_content = f.read()
                doc_reg = re.compile('document\(.*\)', re.DOTALL| re.IGNORECASE)
                if doc_reg.match(file_content):
                        self.doc = eval( file_content )
                        self.set_data( self.doc.ctnt )
                        self.textPad.config( state='normal' )
                        self.textPad.delete('1.0', tki.END )
                        self.textPad.insert( '1.0', self.data )
                        self.textPad.config( state='disabled' )
                        self.old_data = self.data
                        self.curr_file = file
##                        for m in self.doc.mwus:
##                            print( m )
                        self.import_mwu_list( self.doc.ctnt, self.doc.mwus )
                        # attention il faut TOUT importer sinon on ne pourra pas tester
                        self.import_rel_list( self.doc.ctnt, self.doc.rels )
                        self.import_kstruct_list( self.doc.ctnt, self.doc.kstructs )
                else:
                    messagebox.askokcancel('Ok', 'ERROR tentative to import a text only file!' )
##                        file_ident = str(file)
##                        self.doc = document(ident = file_ident, content = file_content)
##                        self.set_data( self.doc.ctnt )               
                self.root.update_idletasks()
               
    def import_Tonly_handler( self ):
        file = filedialog.askopenfilename( parent=self.root, title='Select a file')
        if( (file != None) and (file != '') and (file != ()) ):
            if( self.mwu_vwr is not None ):
                self.mwu_vwr.mwu_vwr_cancel_handler()
            if( self.rel_vwr is not None ):
                self.rel_vwr.rel_vwr_cancel_handler()
            if( self.kstruct_vwr is not None ):
                self.kstruct_vwr.kstruct_vwr_cancel_handler()
            self.all_spans = namelistmap()
            self.all_rels = {}
            self.all_kstructs = {}
            with open(file, mode='r', encoding = 'utf-8') as f:
                file_content = f.read()
                file_ident = str(file)
                self.doc = document(ident = file_ident, content = file_content)
                self.set_data( self.doc.ctnt )
                self.doc.meta = ''
                self.textPad.config( state='normal' )
                self.textPad.delete('1.0', tki.END )
                self.textPad.insert( '1.0', self.data )
                self.textPad.config( state='disabled' )
                self.old_data = self.data
                self.curr_file = file
                self.root.update_idletasks()
        
  
    def text_init( self, text ):
        assert( type( text ) is str )
        self.data = text
        self.doc = None
        if( self.mwu_vwr is not None ):
            self.mwu_vwr.mwu_vwr_cancel_handler()
        if( self.rel_vwr is not None ):
            self.rel_vwr.rel_vwr_cancel_handler()
        if( self.kstruct_vwr is not None ):
            self.kstruct_vwr.kstruct_vwr_cancel_handler()
        self.all_spans = namelistmap()
        self.all_rels = {}
        self.all_kstructs = {}
        self.textPad.config( state='normal' )
        self.textPad.delete('1.0', tki.END )
        self.textPad.insert( '1.0', self.data )
        self.textPad.config( state='disabled' )
        self.curr_file = None

    def document_init( self, doc ):
        assert( type( doc ) == type( document( ident='dummy', content='some text')))
        self.data = doc.ctnt
        self.doc = doc
        if( self.mwu_vwr is not None ):
            self.mwu_vwr.mwu_vwr_cancel_handler()
        if( self.rel_vwr is not None ):
            self.rel_vwr.rel_vwr_cancel_handler()
        if( self.kstruct_vwr is not None ):
            self.kstruct_vwr.kstruct_vwr_cancel_handler()
        self.all_spans = namelistmap()
        self.all_rels = {}
        self.all_kstructs = {}
        self.textPad.config( state='normal' )
        self.textPad.delete('1.0', tki.END )
        self.textPad.insert( '1.0', self.data )
        self.textPad.config( state='disabled' )
        self.curr_file = None

    def python_export( self, file  ):
        self.make_lc_coord_map( self.data )
        with open( file, mode='w+', encoding = 'utf-8') as f:
            f.write( 'document( ident=' + file.__repr__() + ',  content=' + self.data.__repr__() + ', metadata=' + self.doc.meta.__repr__() + ', multi_word_units =' )
            f.write( '[' )
            n = 0
            mwul = []
            for mwu_nm in self.all_spans.get_all_keys():
                if( n > 0 ):
                    f.write( ', ' )
                f.write( 'mwu( nm=\'' + mwu_nm + '\', txtsps=[ ' )
                n += 1
                sp_lst = []
                len_all_spans = len(self.all_spans.get( mwu_nm ))
                span_count = 0
                for sp in self.all_spans.get( mwu_nm ):
                    (lnoffset, coloffset) = self.coordinates( sp.first )
                    first_pos = self.lc_coords_map[ int( lnoffset )-1 ][0] + int( coloffset )
                    (lnoffset, coloffset) = self.coordinates( sp.last )
                    last_pos = self.lc_coords_map[ int(lnoffset)-1 ][0] + int(coloffset)
                    f.write( '(' + str( first_pos ) + ' , ' + str( last_pos ) + ')' )
                    span_count += 1
                    if span_count < len_all_spans:
                        f.write(',')   
                    sp_lst += [ (first_pos, last_pos) ]   
                mwul += [ mwu( nm = mwu_nm , txtsps = sp_lst) ]
                # [ mwu( nm='FAMER_mwu_0', txtsps=[(16, 19)]), ...
                f.write( '])' )
            f.write( '], ')
            f.write( 'relations= [' )
            n = 0
            for r in self.all_rels.keys():
                if( n > 0 ):
                    f.write( ', ' )
                f.write( '{0}'.format( self.all_rels[ r ].__repr__() ))
                n += 1
            f.write( '], constructions= [' )
            n = 0
            for k in self.all_kstructs.keys():
                if( n > 0 ):
                    f.write( ', ' )
                f.write( '{0}'.format( self.all_kstructs[ k ].__repr__() ))
                n += 1
            f.write( '])' )
            f.close()

    def export_TandA_handler( self ):
        file = filedialog.asksaveasfilename( parent=self.root, title='Save file', initialfile=os.path.basename(self.curr_file))
        if( (file != None) and (file != '') and (file != ())):
            # slice off the last character from get, as an extra return is added
            self.data = self.textPad.get( '1.0', tki.END + '-1c' )
            self.python_export( file )
            self.old_data = self.data
            self.curr_file = file

    def export_Tonly_handler( self ):
        file = filedialog.asksaveasfilename( parent=self.root, title='Save file', initialfile=os.path.basename(self.curr_file))
        if( (file != None) and (file != '') and (file != ())):
            # slice off the last character from get, as an extra return is added
            self.data = self.textPad.get( '1.0', tki.END + '-1c' )
            outf = open( file, 'w' )
            outf.write( self.data )
            outf.close()
            self.old_data = self.data
            self.curr_file = file


    def exit_handler( self ):
        self.data = self.textPad.get('1.0', tki.END + '-1c')
        self.root.quit()
        if( self.old_data !=  self.data ):
            if( messagebox.askokcancel('Quit', 'Unsaved content, do you really want to quit?') ):
                self.destroy_auxiliary_root_windows()
                self.root.destroy()
        else:
            self.destroy_auxiliary_root_windows()
            self.root.destroy()

    #---------- construction set handler -------------------------------------

    def kstruct_view_handler( self ):
        if( self.kstruct_vwr is not None ):
            assert( self.kstruct_vwr_on_display )
            if( self.old_all_kstructs != self.all_kstructs ):
                if( messagebox.askokcancel('Save', 'Unsaved constructions, do you really want to quit?') ):
                    file = filedialog.asksaveasfilename( parent=self.root, title='Save file')
        else:
            self.kstruct_vwr = kstruct_viewer( self )

##    def kstruct_edit_handler( self ):
##        if( self.kstruct_editor is not None ):
##            assert( self.kstruct_editor_on_display )
##            if( self.old_all_kstructs != self.all_kstructs ):
##                if( messagebox.askokcancel('Save', 'Unsaved constructions, do you really want to quit?') ):
##                    file = filedialog.asksaveasfilename( parent=self.root, title='Save file')
##        else:
##            self.kstruct_editor = kstruct_editor( self )

    def kstruct_cancel_handler( self ):
        dummy = None

    #--------- top bar menu, help menu  ---------------------------------------	  

    def about_handler( self ):
        label = messagebox.showinfo('About', 'Annotation and Constructions editor for MIROR \n Authors \n Anna Koroleva (koroleva@limsi.fr) & Patrick Paroubek (pap@limsi.fr')

    def clear_view_handler( self ):
        for k in self.all_spans.get_all_keys():
            for m in self.all_spans.get( k ):
                m.hide()

    def refresh_view_handler( self ):
        self.root.update_idletasks()
        
    # -------- mwu, relation source and relation target annotation -------------------------------

    def empty_src( self ):
        l=self.all_spans.get( self.last_SRC_span )
        return( self.all_spans.get( self.last_SRC_span ) is None )

    def empty_trgt( self ):
        return( self.all_spans.get( self.last_TRGT_span ) is None )

    def disambig_submit_handler( self ):
##        print( 'debug1 disambig_value variable is {0} with value {1}'.format( self.disambig_value, self.disambig_value.get() ))
        self.disambig_root.destroy()
        self.disambig_root.quit()

    def multi_text_span_str( self, nm = None, wnts_lst = [] ):
        # a multi_text_span is a name associated to a list of wnts (see class def. above)
        if nm is not None:
            wnts_lst = self.all_spans.get( nm )
        if( (wnts_lst is not None) and (wnts_lst != []) ):
            a_msp = wnts_lst_quicksort( wnts_lst )
            s = ''
            # a wnts is an association between a string id, a first char offset and a last charoffset
            for w in a_msp:
                if s == '':
                    if( nm is not None ):
                        s = nm + ' '
                    else:
                        s = ' '
                s += self.textPad.get( w.first, w.last ) + ' [' + w.first + ', ' + w.last + '] ' 
            return s
        else:
            return ''

    def disambig_select_handler( self ):
##        print( 'debug2 disambig_value variable is {0} with value {1}'.format( self.disambig_value, self.disambig_value.get() ))
        selection = 'You selected the option ' + str( self.disambig_value.get() )
        self.debug_disamb_label.config( text = selection )

    def disambiguator_popup( self, lst = [], disambig_alternative = None ):
        if( disambig_alternative or (len( lst ) > 1) ):
            self.disambig_root = tki.Toplevel()
            self.disambig_root.title( 'disambiguating mwu for selected span' )
            self.disambig_root.protocol("WM_DELETE_WINDOW", self.disambig_submit_handler)
            Label( self.disambig_root, text='Some mwu(s) intersect you selection, please disambiguate').pack()
            # Important for having the radioButton to update the variable, it needs to have a master assigned at creation!
            # here: self.disambig_value = IntVar( master=self.disambig_root )
            self.disambig_value = IntVar( master=self.disambig_root )
            self.disambig_value.set( 0 )
            if( disambig_alternative is not None ):
                assert( type( disambig_alternative is str ) )
                self.disambig_str_lst = [ disambig_alternative ] + lst
            else:
                self.disambig_str_lst = lst

            for i,e in enumerate( self.disambig_str_lst ):
                if( i == 0 ):
                    if( disambig_alternative is not None ):    
                        tmp_s = e
                    else:
                        tmp_s = self.multi_text_span_str( e )
                else:
                    tmp_s = self.multi_text_span_str( e )
                rb = Radiobutton( self.disambig_root, text=tmp_s, value=i, variable=self.disambig_value, command=self.disambig_select_handler).pack()
                self.disambig_value.set( self.disambig_value.get() + 1)
            self.disambig_value.set( 0 )
            #Button( root, text='Submit', command=root.destroy).pack()
            self.debug_disamb_label =  Label( self.disambig_root )
            self.debug_disamb_label.config( text = 'debug selection')
            self.debug_disamb_label.pack( anchor='w' )
            Button( master=self.disambig_root, text='Submit', command=self.disambig_submit_handler).pack() 
            self.disambig_root.mainloop()
            if( disambig_alternative is not None ):
                if( self.disambig_value.get() != 0 ):
                    return self.disambig_str_lst[ self.disambig_value.get() ]
                else:
                    return disambig_alternative
            else:
                if( self.disambig_str_lst > 1 ):
                    return lst[ self.disambig_value.get() ]
                else:
                    if( self.disambig_str_lst > 0 ):
                        return( self.disambig_str_lst[ 0 ] )
                    else:
                        return None
        else:
            return None

    def add_text_span_handler( self ):
        # this is a predicate with side effect, the value returned by the predicate is
        # used in last_src_text_span_handler() or last_trgt_text_span_handler()
        if( self.last_sel_wnts is not None ):
            assert( self.last_sel_wnts.first == self.last_txt_sel_beg )
            assert( self.last_sel_wnts.last == self.last_txt_sel_end )     
        if( intersects( self.curr_span_wnts_lst, self.last_sel_wnts.first,  self.last_sel_wnts.last)):
            self.overlap_select_handler()
            return False
        else:
            self.last_sel_wnts.color( fg=self.new_mwu_fg_color, bg=self.new_mwu_bg_color)
            self.curr_span_wnts_lst.append( self.last_sel_wnts )
            self.feedback_label_text.set( self.curselprompt + self.multi_text_span_str( wnts_lst = self.curr_span_wnts_lst ))
            return True

    def last_src_text_span_handler( self ):
        self.selected_nm = None
        old_src_wnts_lst = self.all_spans.get( self.last_SRC_span )
        if old_src_wnts_lst is not None:    # first, if a source already exists, unmark it
            self.hide_mspan( wnts_lst = old_src_wnts_lst )
        self.hide_mspan( wnts_lst = self.curr_span_wnts_lst )
        self.matched_span_names = self.all_spans.get_key_list_for_matching_items( item_matching_fun = multi_intersects,
                                                                             item_matching_arglist = [ self.curr_span_wnts_lst ] )
        # some text_spans in the span list of the selected source intersect existing mwus
        if( self.matched_span_names != [] ):
            self.curr_sel_str = self.multi_text_span_str( wnts_lst = self.curr_span_wnts_lst )
            self.disambig_alt_str = 'CURRENT SEL = ' + self.curr_sel_str
            self.selected_nm = self.disambiguator_popup( self.matched_span_names, disambig_alternative = self.disambig_alt_str )
            
        if( (self.selected_nm is None) or ( self.selected_nm == self.disambig_alt_str)):
            self.selected_nm = self.name_mgr.create_name( ConstruKT.SRC_TYP )
            self.create_mwu_span( mltspan_nm = self.selected_nm,
                                  curr_widget_mwu_span_lst = self.curr_span_wnts_lst,
                                  typ=ConstruKT.SRC_TYP )
            assert( self.all_spans.get( self.selected_nm ) == self.curr_span_wnts_lst )
        else:
            self.curr_span_wnts_lst = self.all_spans.get( self.selected_nm )
        self.feedback_label_src.set( self.cursrcprompt  + self.selected_nm + self.multi_text_span_str( nm = self.selected_nm  ) )
        if( self.last_SRC_span != ''):
            self.all_spans.remove( self.last_SRC_span )
        self.last_SRC_span = self.selected_nm
        l=self.all_spans.get( self.last_SRC_span )
        assert( not self.empty_src() )
        self.curr_span_wnts_lst = []
        self.feedback_label_text.set( self.curselprompt )        
        if( self.mwu_vwr is not None ):
                self.mwu_vwr.refresh()
        self.color_mspan( nm = self.selected_nm, bgcol=self.bg_new_src_color, fgcol=self.fg_new_src_color  )

    def mark_source( self, wnts_list ):
        # source is marked by a change of text foreground color
        dual_wnts_lst = self.all_spans.get( self.last_TRGT_span )
        if dual_wnts_lst is not None:
            for w in self.curr_span_wnts_lst:
                if intersects( dual_wnts_lst, w.first, w.last ):
                    w.color( bg=self.bg_trgt_color )
                else:
                    w.color( bg=self.bg_src_color )
                w.color( fg=self.fg_src_color )
        else:
            self.color_mspan( wnts_lst = wnts_list, fgcol = self.fg_src_color, bgcol = self.bg_src_color )

    def last_trgt_text_span_handler( self ):
        self.selected_nm = None
        old_trgt_wnts_lst = self.all_spans.get( self.last_TRGT_span )
        if old_trgt_wnts_lst is not None:    # first, if a source already exists, unmark it
            self.hide_mspan( wnts_lst = old_trgt_wnts_lst )
        self.hide_mspan( wnts_lst = self.curr_span_wnts_lst )
        self.matched_span_names = self.all_spans.get_key_list_for_matching_items( item_matching_fun = multi_intersects,
                                                                             item_matching_arglist = [ self.curr_span_wnts_lst ] )
        # some text_spans in the span list of the selected source intersect existing mwus
        if( self.matched_span_names != [] ):
            self.curr_sel_str = self.multi_text_span_str( wnts_lst = self.curr_span_wnts_lst )
            self.disambig_alt_str = 'CURRENT SEL = ' + self.curr_sel_str
            self.selected_nm = self.disambiguator_popup( self.matched_span_names, disambig_alternative = self.disambig_alt_str )
            
        if( (self.selected_nm is None) or ( self.selected_nm == self.disambig_alt_str)):
            self.selected_nm = self.name_mgr.create_name( ConstruKT.TRGT_TYP )
            self.create_mwu_span( mltspan_nm = self.selected_nm,
                                  curr_widget_mwu_span_lst = self.curr_span_wnts_lst,
                                  typ=ConstruKT.TRGT_TYP )
            assert( self.all_spans.get( self.selected_nm ) == self.curr_span_wnts_lst )
        else:
            self.curr_span_wnts_lst = self.all_spans.get( self.selected_nm )
        self.feedback_label_trgt.set( self.cursrcprompt  + self.selected_nm + self.multi_text_span_str( nm = self.selected_nm  ) )
        if( self.last_TRGT_span != ''):
            self.all_spans.remove( self.last_TRGT_span )
        self.last_TRGT_span = self.selected_nm
        l=self.all_spans.get( self.last_TRGT_span )
        assert( not self.empty_trgt() )
        self.curr_span_wnts_lst = []
        self.feedback_label_text.set( self.curselprompt )        
        if( self.mwu_vwr is not None ):
                self.mwu_vwr.refresh()
        self.color_mspan( nm = self.selected_nm, bgcol=self.bg_new_trgt_color, fgcol=self.fg_new_trgt_color  )
            
    def mark_target( self, wnts_list ):
        # target is marked by a change of text background color
        dual_wnts_lst = self.all_spans.get( self.last_SRC_span )
        if dual_wnts_lst is not None:
            for w in wnts_list:
                if intersects( dual_wnts_lst, w.first, w.last ):
                    w.color( fg=self.fg_src_color )
                else:
                    w.color( fg=self.fg_trgt_color )
                w.color( bg=self.bg_trgt_color )    
        else:
            self.color_mspan( wnts_lst = wnts_list, fgcol = self.fg_trgt_color, bgcol = self.bg_trgt_color )

    def overlap_select_handler( self ):
        messagebox.showinfo(title='WARNING:', message='Text spans of a multi-word unit cannot overlap! Ignoring last selection.')

    def cancel_handler( self):
        print( 'done' )

    def create_mwu_span( self, mltspan_nm='', curr_widget_mwu_span_lst = None, typ = '' ):
        # curr_span_wnts_lst is None when the mwu span is created by an annotation algorithm, not from the interface main window
        assert( type( mltspan_nm ) is str )
        assert( mltspan_nm != '' )
        if( curr_widget_mwu_span_lst is not None ):
            for s in curr_widget_mwu_span_lst:
                s.set_type( typ )
            self.matched_span_names = self.all_spans.get_key_list_for_matching_items( item_matching_fun = equal_span_and_type,
                                                                                      item_matching_arglist = [ curr_widget_mwu_span_lst ] )
            # if some text_spans in the span list of the selected source have exactly the same span and type
            # as the one that we want to create we do not duplicate the mwu.
            if( self.matched_span_names != [] ):
                self.last_MWU_span = self.matched_span_names[ 0 ] # taking the first if many is as good as any, provided I always take the first
                if( self.last_MWU_span in self.mwu_alias_table.get_all_keys()):
                    # we make sure that mltspan_nm is in the alias list of self.last_MWU_span
                    if( mltspan_nm not in self.mwu_alias_table.get( self.last_MWU_span )):
                        self.mwu_alias_table.add( self.last_MWU_span, mltspan_nm )
                    # else nothing to do mltspan_nm is already in the list of aliases of self.last_MWU_span
                else:
                    self.mwu_alias_table.add( self.last_MWU_span, mltspan_nm  )
            else:
                assert( len( curr_widget_mwu_span_lst ) > 0 )
                self.all_spans.set( mltspan_nm, curr_widget_mwu_span_lst )
                self.last_MWU_span = mltspan_nm

    def type_text_span_submit_handler(self):
        self.textPad.tag_delete( 'sel'  )
        # the last mwu has received a type
        cat = self.mwu_category.get()
        if( cat == 0 ):
            mltspan_nm = self.name_mgr.create_name(  ConstruKT.MWU_TYP  )
            tp = self.last_MWU_type_var.get()
            if( (tp is None) or (tp == '')):
                tp = ConstruKT.MWU_TYP
            self.create_mwu_span( mltspan_nm=mltspan_nm, curr_widget_mwu_span_lst=self.curr_span_wnts_lst, typ=tp )
            self.hide_mspan( wnts_lst = self.all_spans.get( self.last_MWU_span ) )
            self.curr_span_wnts_lst = []
##            if( not self.empty_trgt() ):
##                self.hide_mspan( wnts_lst = self.all_spans.get( self.last_TRGT_span ) )
##                self.feedback_label_src.set( self.curtrgtprompt )
##            if( not self.empty_src() ):
##                self.hide_mspan( wnts_lst = self.all_spans.get( self.last_SRC_span ) )
##                self.feedback_label_src.set( self.cursrcprompt )
            if( self.last_text_span_popup_root is not None ):
                self.last_text_span_popup_root.quit()
                self.last_text_span_popup_root.destroy()
                self.last_text_span_popup_root = None
            self.feedback_label_text.set( self.curselprompt )
            self.color_mspan( nm = mltspan_nm, bgcol=self.mwu_bg_color, fgcol=self.mwu_fg_color  )
            if( self.mwu_vwr is not None ):
                self.mwu_vwr.refresh()
        else:
            if( cat == 1 ):   # a source
                self.last_src_text_span_handler()
            else:
                assert( cat == 2 )  # a target
                self.last_trgt_text_span_handler()
            # close the last mwu category (mwu - with type input- or src or target) input popup window  
            if( self.last_text_span_popup_root is not None ):
                self.last_text_span_popup_root.quit()
                self.last_text_span_popup_root.destroy()
                self.last_text_span_popup_root = None
            self.feedback_label_text.set( self.curselprompt )
            if( (not self.empty_src()) and (not self.empty_trgt()) ):
                self.create_rel_handler()
        self.text_sel_on = True
 
    def type_text_span_cancel_handler(self):
        if( self.last_MWU_span != '' ):
            self.hide_mspan( wnts_lst = self.all_spans.get( self.last_MWU_span ) )
            self.all_spans.remove( nm = self.last_MWU_span )
        else:
            self.hide_mspan( wnts_lst = self.curr_span_wnts_lst )
        self.curr_span_wnts_lst = []
        self.feedback_label_text.set( self.curselprompt )
        self.last_text_span_popup_root.destroy()
        self.last_text_span_popup_root.quit()
        self.last_text_span_popup_root = None
        self.text_sel_on = True

    def select_mwu_cat_handler( self ):
        selection = 'You selected the mwu category ' + str( self.mwu_category.get() )
        
    def last_text_span_handler( self ):
        if self.add_text_span_handler(): # if True, this test has the side effect of adding the last selected span in the current selection list
            self.textPad.tag_delete( 'sel'  )
            self.last_text_span_popup_root = tki.Toplevel()
            self.last_text_span_popup_root.title( 'last text span type selection' )
            self.last_text_span_popup_root.protocol( "WM_DELETE_WINDOW", self.type_text_span_cancel_handler )
            self.mwu_category = IntVar( master=self.last_text_span_popup_root )
            Radiobutton( self.last_text_span_popup_root, text='Multi-word unit', value=0, variable=self.mwu_category, command=self.select_mwu_cat_handler).pack()
            Radiobutton( self.last_text_span_popup_root, text='Relation source', value=1, variable=self.mwu_category, command=self.select_mwu_cat_handler).pack()
            Radiobutton( self.last_text_span_popup_root, text='Relation target', value=2, variable=self.mwu_category, command=self.select_mwu_cat_handler).pack()
            Label( self.last_text_span_popup_root, text='Type' ).pack( side='left' )
            self.last_MWU_type_var = StringVar( master = self.last_text_span_popup_root )
            Entry( master=self.last_text_span_popup_root, textvariable = self.last_MWU_type_var ).pack( side='left')
            Button( master=self.last_text_span_popup_root, text='Submit', command=self.type_text_span_submit_handler).pack(side='bottom')
            Button( master=self.last_text_span_popup_root, text='Cancel', command=self.type_text_span_cancel_handler).pack(side='bottom')
            self.text_sel_on = False
            self.last_text_span_popup_root.mainloop()

    def relation_label_handler( self ):
        print( 'relation_label {0}, {1}'.format( self.last_txt_sel_beg, self.last_txt_sel_end ))

    #--- popup for viewer for displaying all mwus. ---
        
    def show_mwu_cancel_handler( self ):
        self.mwu_vwr.__del__()
        self.mwu_vwr = None

    def show_mwu_refresh_handler( self ):
        self.mwu_vwr.refresh()

    def show_mwu_clear_view_handler( self ):
        self.mwu_vwr.clear_view()

    def mwu_handler( self ):
        if( self.mwu_vwr is None ):
            scrn_w = self.root.winfo_screenwidth()
            width = scrn_w/4
            x = (scrn_w/2) - (width/2)
            scrn_h = self.root.winfo_screenheight()
            height = scrn_h/4
            y = (scrn_h/2) - (height/2)
            self.mwu_vwr = mwu_viewer( self, x, y )
            self.mwu_vwr.run()
        else:
            self.mwu_vwr.refresh()
            
    #--- popup for viewer for displaying all rels. ---

    def rel_handler( self ):
        if( self.rel_vwr is None ):
            scrn_w = self.root.winfo_screenwidth()
            width = scrn_w/4
            x = (scrn_w/2) - (width/2)
            scrn_h = self.root.winfo_screenheight()
            height = scrn_h/4
            y = (scrn_h/2) - (height/2)
            self.rel_vwr = rel_viewer( self, x, y )
            self.rel_vwr.run()
        else:
            self.rel_vwr.refresh()
            
    #--- popup for viewer for displaying metadata. ---
    def meta_view_handler( self ):
        if( self.meta_vwr is None ):
            print( 'meta is None in ConstruKT')
##            top = Toplevel(master = self.meta_vwr_root)
##            top.title("About this application...")
##
##            msg = Message(top, text=self.doc.meta)
##            msg.pack()
            self.meta_vwr = meta_vwr( self )
            self.meta_vwr = None #when the interaction loop has finished.

    #--- popup for viewer for editing a construction set ---
        
    def kstruct_cancel_handler( self ):
        if( self.kstruct_vwr_on_display ):
            self.kstruct_vwr.__del__()

    def kstruct_refresh_handler( self ):
        self.kstruct_vwr.refresh()

    #-------- relation creation -------------------------
        
##    def relation_handler( self ):
##        print( 'relation handler {0}, {1}'.format( self.last_txt_sel_beg, self.last_txt_sel_end ))
##        
    def hide_mspan( self, nm = None, wnts_lst = None):
        if( nm is not None ):
            wnts_lst = self.all_spans.get( nm )
        if( wnts_lst  is not None ): # Note: it can be None during manual creation of a mwu.
            for w in wnts_lst:
                assert( w.txtwid == self.textPad )
                w.hide()

    def color_mspan( self, nm = None, wnts_lst = [], fgcol = None, bgcol = None):
        if( nm is not None ):
            wnts_lst = self.all_spans.get( nm )
##        print( 'DEBUG==>in color_mspan,  wnts_lst={0}'.format( wnts_lst ))
        for w in  wnts_lst:
            assert( w.txtwid == self.textPad )
            if( w.id not in self.textPad.tag_names() ):
                w.show()
            if fgcol is not None:
                if bgcol is not None:
                    w.color( fg=fgcol, bg=bgcol )
                else:
                    w.color( fg=fgcol )
            else:
                if bgcol is not None:
                    w.color( bg = bgcol )
                #else do nothing
        self.textPad.tag_raise( w.id )

    def done_select_handler( self ):
        self.dummy = None
        self.last_sel_wnts = None
        self.master_app.refresh()
 
    def unmark_text_span_handler( self ):
        sel_first = self.textPad.index( self.last_txt_sel_beg )       
        sel_last = self.textPad.index( self.last_txt_sel_end )
        self.last_sel_wnts.color( bg=self.default_bg_color )
        self.textPad.tag_delete( self.last_sel_wnts.id )
        self.textPad.tag_delete( 'sel' )

        if( (self.curr_span_wnts_lst is not None) and (intersects( self.curr_span_wnts_lst, sel_first, sel_last ))):
            for s in self.curr_span_wnts_lst:
                s.hide() # we need to address each individual wnts since the mwu has not been created yet.
            self.feedback_label_text.set( self.curselprompt )
            self.curr_span_wnts_lst = []
        
        lst_src = self.all_spans.get( self.last_SRC_span )
        if((lst_src is  not None) and (intersects( lst_src, sel_first, sel_last ))):
            self.hide_mspan( nm = self.last_SRC_span )
            self.feedback_label_src.set( self.cursrcprompt )
            self.all_spans.remove( self.last_SRC_span )
            self.last_SRC_span = ''

        lst_trgt = self.all_spans.get( self.last_TRGT_span )    
        if( (lst_trgt is  not None) and intersects( lst_trgt,  sel_first, sel_last  )):
            self.hide_mspan( nm = self.last_TRGT_span )
            self.feedback_label_trgt.set( self.cursrcprompt )
            self.all_spans.remove( self.last_TRGT_span )
            self.last_TRGT_span = ''

        # NOTE!: here unmark() should not concern mwu that have been finalized
        # if one want to hide these, one should use the "hide" functionality
        # accessible throughout the main mwu menu,
        # or to delete them from the same mwu menu.
   
    # ----------- relation creation (when both the source and target mwu unit haved been chosen).----------------------

    def create_relation( self, n = None, s = None, t = None, typ='' ):
        # relations  are always  created from an existing source and target mwu
        # Note that  the type may be an empty string
        assert( type( s ) is str )
        assert( s != '' )
        assert( type( t ) is str )
        assert( t != '' )
        k = self.mwu_alias_table.get_key_for( s )
        if( k is not None ):
            self.new_src = k
        else:
            self.new_src = s
        k = self.mwu_alias_table.get_key_for( t )
        if( k is not None ):
            self.new_trgt = k
        else:
            self.new_trgt = t
        if( n is None ):
            self.last_rel_nm = self.name_mgr.create_name( ConstruKT.REL_TYP )
        else:
            self.last_rel_nm = n
        new_rel = rel( nm = self.last_rel_nm, source = self.new_src, target = self.new_trgt, tp = typ )
        self.all_rels[ self.last_rel_nm ] = new_rel

    def type_rel_submit_handler( self ):
            rel_typ = self.last_REL_type_var.get()
            self.create_relation( s=self.last_SRC_span, t=self.last_TRGT_span, typ=rel_typ )
            self.feedback_label_src.set( self.curtrgtprompt )
            self.feedback_label_trgt.set( self.curtrgtprompt )
            self.color_mspan( wnts_lst = self.all_spans.get( self.last_SRC_span ), bgcol=self.bg_src_color, fgcol=self.fg_src_color )
            self.color_mspan( wnts_lst = self.all_spans.get( self.last_TRGT_span ), bgcol=self.bg_trgt_color, fgcol=self.fg_trgt_color )
            self.create_rel_popup_root.quit()
            self.last_SRC_span = '' 
            self.last_TRGT_span = ''
            if( self.rel_vwr is not None ):
                self.rel_vwr.refresh()
            if( self.mwu_vwr is not None ):
                self.mwu_vwr.refresh()
                
    def type_rel_cancel_handler( self ):
            if( not self.empty_src() ):
                  self.hide_mspan( wnts_lst = self.all_spans.get( self.last_SRC_span ) )
                  self.all_spans.remove( nm = self.last_SRC_span )
                  self.feedback_label_src.set( self.cursrcprompt )
            if( not self.empty_trgt() ):
                  self.hide_mspan( wnts_lst = self.all_spans.get( self.last_TRGT_span ) )
                  self.all_spans.remove( nm = self.last_TRGT_span )
                  self.feedback_label_trgt.set( self.curtrgtprompt )
            self.create_rel_popup_root.quit()

    def create_rel_handler( self ):
            assert( self.last_TRGT_span is not None )
            assert( self.last_SRC_span is not None )
            self.create_rel_popup_root = tki.Toplevel()
            self.create_rel_popup_root.title( 'New relation type' )
            self.create_rel_popup_root.protocol( "WM_DELETE_WINDOW", self.type_rel_cancel_handler )
            Label( self.create_rel_popup_root, text='Type' ).pack( side='left' )
            self.last_REL_type_var = StringVar( master = self.create_rel_popup_root )
            Entry(  master=self.create_rel_popup_root, textvariable = self.last_REL_type_var ).pack( side='left')
            Button( master=self.create_rel_popup_root, text='Submit', command=self.type_rel_submit_handler).pack(side='bottom')
            Button( master=self.create_rel_popup_root, text='Cancel', command=self.type_rel_cancel_handler).pack(side='bottom')
            self.create_rel_popup_root.mainloop()
            # WARNING: destroy must be here because there are two pop-up window opened last_text_span_handler and relation_type_handler)
            # otherwise the destroy associated to the last pop-up generates and error since the first pop-up is still present on the screen
            if( self.create_rel_popup_root is not None ):
                self.create_rel_popup_root.destroy()
            self.create_rel_popup_root = None

    def remove_referring_rels( self, mwu_id ):
        for rid in list(self.all_rels.keys()):
            src = self.all_rels[ rid ].src
            trgt = self.all_rels[ rid ].trgt
            if(( src == mwu_id ) or (trgt == mwu_id)):
                if( src == mwu_id ):
                    other_mwu = trgt
                else:
                    other_mwu = src
                # first we unmark the relation if it is displayed on the main window
                self.hide_mspan( wnts_lst = self.all_spans.get( other_mwu ) )
                # then we remove the referring rels, the src and trgt are left as is.
                self.all_rels.pop( rid )

    def make_listbox_rel_repr( self, r ):
        if( r.typ is None ):
             curr_rel_repr = '{0} '.format( repr( r.name ) ).replace( '\'', '')
        else:
            curr_rel_repr = '{0} {1}'.format( repr( r.name ), repr( r.typ) ).replace( '\'', '')
        #---text represenation of all mwus of source
        for wnt in wnts_lst_quicksort( self.all_spans.get( r.src )):
            # to have all the text in one line in order to use the relation_viewer lines as index for rel selection
            flpos,fcpos = self.coordinates( wnt.first )
            llpos,lcpos = self.coordinates( wnt.last ) 
            txtsp = self.textPad.get( wnt.first, wnt.last ).replace( '\n', ' ')
            curr_rel_repr += ' {0} <L_{1}, C_{2}>{3}<L_{4},C_{5}>'.format( wnt.typ, flpos, fcpos, txtsp, llpos, lcpos )
        #---built text represenation of  all mwus of target
        for wnt in wnts_lst_quicksort( self.all_spans.get( r.trgt )):
            # to have all the text in one line in order to use the mwu_textPad lines as index for mwu selection
            flpos,fcpos = self.coordinates( wnt.first )
            llpos,lcpos = self.coordinates( wnt.last ) 
            txtsp = self.textPad.get( wnt.first, wnt.last ).replace( '\n', ' ')
            curr_rel_repr += ' {0} <L_{1}, C_{2}>{3}<L_{4},C_{5}>'.format( wnt.typ, flpos, fcpos, txtsp, llpos, lcpos )
        return( curr_rel_repr )
    
#----- end of TkInterApp class 
        



