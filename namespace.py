
class nametype():
    def __init__( self, typ ):
        assert( type( typ ) is str )
        self.label = typ
        self.maxid = 0
        self.all_names = []
        self.reset_maxid = 0 # used only when reseting all the names of a type
        self.old2new_name_mapping = {}

    def __del__( self ):
        dymmy = None

    def __repr__( self ):
        sout = '===namestype==\n'
        return( sout )

    def __repr__( self ):
          return( '<namespace: >' )

    def create_name( self  ):
        l =  self.label + '_' + ( '%d' %  self.maxid )
        self.maxid += 1
        while(  l in self.all_names ):
              self.maxid += 1
              l =  self.label + '_' + ( '%d' %  self.maxid )
        self.all_names.append( l )
        return( l )

    def add_name( self, nm ):
        self.all_names.append( nm )

    def rename( self, old_nm, new_nm ):
        self.all_names[ self.all_names.index( old_nm )] = new_nm
    
    def create_replacement_name( self ):
        l =  self.label + ( '%d' %  self.reset_maxid )
        self.reset_maxid += 1
        assert( l not in self.old2new_name_mapping.keys() )
        return( l )

    def reset_names( self ):
        self.old2new_name_mapping = {}
        self.reset_maxid = 0
        for n in self.all_names:
            new_n = self.create_replacement_name()
            self.all_names[ self.all_names.index( n ) ] = new_n
            self.old2new_name_mapping[ n ] = new_n
            self.reset_maxid += 1
        self.maxid = self.reset_maxid
        return( self.old2new_name_mapping )
              
#--- end of class nametype -----

class namespace( ):
    def __init__( self, typelist = [] ):
        self.all_types = {}
        for t in typelist:
            self.add_type( t )

    def __str__( self ):
        sout = '===namespace==\n'
        sout += '====='
        return( sout )

    def __repr__( self ):
        return( '<namespace: >' )

    def add_type( self, typ ):
        if typ not in self.all_types:
            self.all_types[ typ ] = nametype(  typ )

    def remove_type( self, typ ):
        del self.all_types[ typ ]

    def create_name( self, typ ):
        return( self.all_types[ typ ].create_name() )

    def which_name_type( self, nm, typ = None ):
        # can be used also as an existence predicate
        if( typ is None ):
            for t in self.all_types.keys():
                if( nm in self.all_types[ t ].all_names ):
                    return( t )
            return( None )
        else:
            if( nm in self.all_types[ typ ].all_names ):
                return( typ )
            else:
                return None

    def add_name( self, nm, typ = None ):
        t = self.which_name_type( nm )
        if( t in self.all_types.keys() ):
            print( 'ERROR the name {} with name type {} cannot be added because it already exists!'.format(  nm, typ ))
            assert( 0 ) 
        else:
            assert( typ in self.all_types.keys() )
            self.all_types[ typ ].add_name( nm ) 

    def rename( self, old_nm, new_nm, typ = None):
        if( typ is None ):
             for t in self.all_types.keys():
                if( old_nm in self.all_types[ t ].all_names ):
                    self.all_types[ t ].rename( old_nm, new_nm )
        else:
            if( self.which_name_type( old_nm, typ ) is not None ):
                self.all_types[ typ ].rename( old_nm, new_nm )

    def remove_name( self, nm, typ = None ):
        if( typ is None ):
            for t in self.all_types.keys():
                if( nm in self.all_types[ t ].all_names ):
                    self.all_types[ t ].all_names.remove( nm )
        else:
            if( nm in self.all_types[ typ ].all_names ):
                self.all_types[ typ ].all_names.remove( nm )

    def reset_names( self, typ = None ):
        if( typ is None ):
            self.name_mapping = {}
            for t in self.all_types.keys():
                m = self.all_types[ t ].reset_names()
                self.name_mapping = { **self.name_mapping, **m }
            return( self.name_mapping )
        else:
            if( typ in self.all_types ):
                return( self.all_types[ typ ].reset_names() )
                    
#--- end of class namespace ---
                
#DEMO = True
DEMO = False           
if DEMO:
    s = namespace()
    print( '--------- creating types --------' )
    s.add_type( 'footype' )
    s.add_type( 'bartype' )
    print( '--------- creating names ---------' )
    n1 = s.create_name( 'footype' )
    print( 'n1= {0}'.format( n1 ))
    n2 = s.create_name( 'bartype' )
    print( 'n2= {0}'.format( n2 ))
    print( 's.which_name_type( n1, \'footype\' )= {0}'.format( s.which_name_type( n1, 'footype' )))
    print( 's.which_name_type( n2 )= {0}'.format( s.which_name_type( n2 )))
    print( 's.which_name_type( \'zoo\', \'footype\' )= {0}'.format( s.which_name_type( 'zoo', 'footype' )))
    print( 's.which_name_type( \'zoo\' )= {0}'.format( s.which_name_type( 'zoo' )))
    print( '-----------' )
    print( 'trying to rename n1 into new_n1 with the wrong bartype' )
    print( 'new_n1 = \'new_\' + n1')
    new_n1 = 'new_' + n1
    s.rename( n1, new_n1, 'bartype' )
    print( 's.which_name_type( n1 )= {0}'.format( s.which_name_type( n1 )))
    print( 's.which_name_type( new_n1 )= {0}'.format( s.which_name_type( new_n1 )))
    print( 'renaming n1 into new_n1' )
    s.rename( n1, new_n1, 'footype' )
    print( 's.which_name_type( n1, \'footype\' )= {0}'.format( s.which_name_type( n1, 'footype' )))
    print( 's.which_name_type( new_n1, \'footype\' )= {0}'.format( s.which_name_type( new_n1, 'footype' )))
    print( 'renaming n2' )
    print( 'new_n2 = \'NEW_\' + n2')
    new_n2 = 'NEW_' + n2
    s.rename( n2, new_n2 )
    print( 's.which_name_type( n2, \'footype\' )= {0}'.format( s.which_name_type( n2, 'footype')))
    print( 's.which_name_type( new_n2 )= {0}'.format( s.which_name_type( new_n2 )))
    print( '-------resetting names of for the type footype ---' )
    print( s.reset_names( 'footype' ))
    print( 's.which_name_type( n1 )= {0}'.format( s.which_name_type( n1 )))
    print( 's.which_name_type( new_n1 )= {0}'.format( s.which_name_type( new_n1 )))
    print( 's.which_name_type( n2 )= {0}'.format( s.which_name_type( n2 )))
    print( 's.which_name_type( new_n2 )= {0}'.format( s.which_name_type( new_n2 )))
    print( '-------resetting names of the whole name space ---' )
    print( s.reset_names() )
    print( 's.which_name_type( n1 )= {0}'.format( s.which_name_type( n1 )))
    print( 's.which_name_type( new_n1 )= {0}'.format( s.which_name_type( new_n1 )))
    print( 's.which_name_type( n2 )= {0}'.format( s.which_name_type( n2 )))
    print( 's.which_name_type( new_n2 )= {0}'.format( s.which_name_type( new_n2 )))
    print( '----------' )
    print( 'removing n1' )
    s.remove_name( n1, 'footype' )
    print( 's.which_name_type( n1, \'footype\' )= {0}'.format( s.which_name_type( n1, 'footype' )))
    print( 'removing n2' )    
    s.remove_name( n2 )
    print( 's.which_name_type( n2 )= {0}'.format( s.which_name_type( n2 )))
    

    
