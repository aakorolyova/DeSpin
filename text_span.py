import sys
import glob
import codecs
import os
import collections
import io
    
class mwu( object ):
    #--- class variables 
    default_mwu_name_prefix = 'MWU'
    default_mwu_cnt = 0
    # txsps is a list of pairs of character offsets e.g.  mwu( nm='MWU_4', txtsps=[ (13300 , 13320)])
    # example of mwu structure:
    # m1=mwu( nm='MWU_4', txtsps=[ (13300 , 13320)], annots={'comments':'ceci est un test', 'POS_GRACE':'Ncms'})
    def __init__( self, nm = None, txtsps = [], tp = '', annots = {} ):
        assert( type( txtsps ) is list )
        #--- name.
        if( nm is None ):
            self.name = mwu.default_mwu_name_prefix + '_' + str( mwu.default_mwu_cnt ); mwu.default_mwu_cnt += 1
        else:
            self.name = nm
        self.txtspans = txtsps
        #--- annotations global to the mwu (attribute value associations in a dictionary).
        self.annotations = annots
        self.typ = tp

    def text_n( self, doc, n ):
        tsp = self.txtspans[ n ]
        assert( type( tsp ) is tuple )
        return( doc.span( tsp[0], tsp[1] ))
                
    def text( self , doc, sep = None ):
        res = ''
        for i in range( 0, len( self.txtspans ) ):
                if( sep is None ):
                    res += self.text_n( doc, i )
                else:
                    if( i > 0 ):
                        res += sep
                    res += self.text_n( doc, i )  
        return( res )

    def span_n( self, n ):
        if( n < len( self.txtspans) ):
            return( self.txtspans[ n ] )
        else:
            return( None )

    def __repr__( self ):
        res = 'mwu( nm=' + self.name.__repr__() +  ', txtsps=['
        n = 0
        for sp in self.txtspans:
            res += sp.__repr__()
            ##            res += 'wnts( \'SPAN\', ' +  str( sp[0] ) + ',' + str( sp[1] ) + ')'
            n += 1
            if( n < len( self.txtspans )):
                res += ', '
        res +=  '])'
        return( res ) 

    def __str__( self ):
        res = '---mwu:\n\tname= ' + str( self.name )
        res += '\n\ttextspans is: ' + str( self.txtspans )
        res += '\n\tannotations is: ' + str( self.annotations )
        res += '\n'
        return( res )

    def size( self ):
        return( len( self.txtspans ) )
    
         #---- annotations of the whole mwu)
    def set_annot( self, aspect, value ):
        self.annotations[ aspect ] = value

    def get_annot( self, aspect ):
        return( self.annotations[ aspect ] )
        
#--- end of mwu class

class rel( object ):
    def __init__( self, nm = '', source = None, target = None, tp = None ):
        assert( type( nm ) is str )
        self.name = nm # a string identifier for the relation
        self.src = source # an identifier in all_span data member of ConstruKT instance
        self.trgt = target # an identifier in all_span data member of ConstruKT instance
        self.typ = tp

    def __repr__( self ):
        res = 'rel( nm=' + self.name.__repr__() + ', source=' +  self.src.__repr__() + ', target=' + self.trgt.__repr__() + ', tp=' + self.typ.__repr__() + ')'
        return( res )

    def __str__( self ):
        sout = 'rel: name= ' + str(self.name) + ' typ= ' +  str(self.typ) + ' src= ' +  str(self.src)  + ' trgt= ' + str(self.trgt) + '\n'
        return( sout )

class relation( rel ):
    # NOTE: not yet used
    def __init__( self, nm='', src=None, trg=None, annotations = {}, typ = None ):
         assert( type( nm) is str )
         assert( type( src ) is mwu )
         assert( type( trg ) is mwu )
         rel.__init__( self, nm, src.name, trg.name, typ )
         self.source = src
         self.target = trg
         self.annotations= annotations

     #---- annotations of the whole mwu)
    def set_annot( self, aspect, value ):
        self.annotations[ aspect ] = value

    def get_annot( self, aspect ):
        return( self.annotations[ aspect ] )
    

#--- end of class relation    

class construction( ):
    def __init__( self, nm = None, rel_lst = [] ):
        assert( type( nm ) is str )
        self.name = nm
        self.rels = rel_lst

    def __repr__( self ):
        sout = 'construction( nm=' +  self.name.__repr__() + ', rels=['
        n = 0
        for r in self.rels:
            sout += r.__repr__()
            n += 1
            if( n < len( self.rels ) ):
                sout += ', '
        sout += ']'
        return( sout )  

    def __str__( self ):
        sout = 'construction: name= ' + str(self.name) + 'rels='
        for r in self.rels:
            sout += r.__str__()
        sout += '\n'
        return( sout )   
    
#--- end of class construction

class document():
    def __init__(self, ident=None, content='', metadata='', multi_word_units=[], relations=[], constructions=[] ):
        if( (type(ident) is None) or (type(ident) is not str) ):
            raise ValueError
        else:
             self.id = ident
            
        if( type(metadata) is not str ):
            raise ValueError
        else:
             self.meta = metadata
            
        if(  type(content) is not str ):
             raise ValueError
        else:
             self.ctnt = content
        # potentialy a document has multi-word units (mwus) annotations, relations (between two mwus, a source and a target) and constructions (sets of relations)
        self.mwus = multi_word_units
        self.rels = relations
        self.kstructs = constructions

    def len( self ):
        return( len( self.ctnt ) )

    def byte_len( self ):
        return( len( self.ctnt.encode('utf8') ))

    def content( self ):
        return( self.ctnt )

    def span( self, first, last ):
        return( self.ctnt[ first:last ] )

    def __repr__( self ):
        res = 'document( ident=\'' + self.id + '\''
        res += '\t\n, content=' + self.ctnt.__repr__()
        res += '\t\n, metadata=' + self.meta.__repr__()
        res += '\t\n, multi_word_units = ['
        i=0
        for m in self.mwus:
            if( i > 0 ):
                res += ', '
            i += 1
            res += m.__repr__()
        res += ']\n'
        res += '\t, relations= ['
        i = 0
        for r in self.rels:
            if( i > 0 ):
                res += ', '
            i += 1
            res += r.__repr__()
        res += ']\n'
        res += '\t, constructions= ['
        i = 0
        for k in self.kstructs:
            if( i > 0 ):
                res += ', '
            i += 1
            res += k.__repr__()
        res += '] )\n'
        return( res )

    def __str__( self ):
        res = 'document is:' + '\tid= ' + str( self.id )
        res += '\tmeta= ' + str( self.meta )
        res += '\tlen(self.ctnt)= ' + str( len( self.ctnt ))
        res += '\tlen(mwus)=' + str( len(self.mwus) )
        res += '\tlen(rels)=' + str( len(self.rels) )
        return( res )

    #------- file io

    def read( self, path ):
        assert( (type( path ) is str) and (path != '') )
        buffer_sz = 100
        in_strm = codecs.open( path, mode='r', encoding='utf-8', errors='strict', buffering = -1)
        assert( in_strm )
        in_data = u''
        for l in in_strm.readlines( buffer_sz ):
            in_data += l
        self.ctnt = self.ctnt + in_data
        in_strm.close()

    def write( self, path ):
        assert( (type( path ) is str) and (path != '') )
        out_strm = codecs.open( path, mode='w', encoding='utf-8', errors='strict', buffering = -1)
        assert( out_strm )
        out_strm.write( self.ctnt )
        out_strm.close()

    #--- mwus

    def set_mwu( self, m = [] ):
        assert( type( m ) is list )
        for e in m:
            assert( type( e ) is mwu )
        self.mwus =  m

    def add_mwu( self, m ):
        assert( (type( m ) is mwu) or (type(m) is list) )
        if( type( m ) is list ):
            self.mwus.extend( m )
        else:
            self.mwus += [ m ]

    def remove_mwu( self, m ):
        assert( (type( m ) is mwu) or (type(m) is list) )
        if( type( m ) is list ):
            for e in m:
                self.mwus.remove( e )
        else:    
            self.mwus.remove( m )

    def get_mwus( self ):
        return( self.mwus )

    def find_mwu_containing_span( self, s ):
        assert( (type( s ) is tuple) and (len(s) == 2) and (type(s[0]) is int) and (type(s[1]) is int) and (s[0] < s[1]) )
        for m in self.mwus:
                if( m.contains_span_p( s ) ):
                    return( m )
        return( None )

    #--- relations 

    def set_rel( self, r = [] ):
        assert( type( r ) is list )
        for e in r:
            assert( type( e ) is relation )
        self.rels =  r

    def add_rel( self, r ):
        assert( (type( r ) is relation) or (type(r) is list) )
        if( type( r ) is list ):
            self.rels.extend( r )
        else:
            self.rels += [ r ]

    def remove_rel( self, r ):
        assert( (type( r ) is relation) or (type(r) is list) )
        if( type( m is list ) ):
            for e in r:
                self.rels.remove( e )
        else:    
            self.rels.remove( r )

    def get_rels( self ):
        return( self.rels )
    
#--- end of class document
