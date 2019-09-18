# HAMT map
# see https://en.wikipedia.org/wiki/Hash_array_mapped_trie
# Install: > pip3 install pyrsistent

#synopsis: a map that maps "names" to lists of items, each item is unique (e.g. a physical location),
# but may appear in several list associated to different names.
# The map manages the reverse mapping (one item mapped to all the names it is associated with),
# and in case case of ambiguity uses a disambiguating
# function to associate only one name to the item (a default disambiguating function which takes
# the first name is provided). It is redefinable when initializating the map.
# Removal of one name removed all the corresponding associations, similarly removing one
# item will impact all the names which have this item in their map (target) list.

# Demo:
# >>> exec(open('namelistmap.py').read())
# >>> exec(open('test.py').read())
# exec(open('namelistmap.py').read())
# ---x---
# x=namelistmap()
# ===direct map==
# ===reverse map===
# =====
# x.set( 'foo', [2, 3, 4] )
# ===direct map==
# foo --> [2, 3, 4]
# ===reverse map===
# 2 --> ['foo']
# 3 --> ['foo']
# 4 --> ['foo']
# =====
# ['foo']
# foo
# -----
# ===direct map==
# foo --> [2, 3, 4]
# ===reverse map===
# 2 --> ['foo']
# 3 --> ['foo']
# 4 --> ['foo']
# =====
# x.set( 'bar', [1, 3, 7] )
# ===direct map==
# foo --> [2, 3, 4]
# bar --> [1, 3, 7]
# ===reverse map===
# 2 --> ['foo']
# 3 --> ['foo', 'bar']
# 4 --> ['foo']
# 1 --> ['bar']
# 7 --> ['bar']
# =====
# ['foo', 'bar']
# foo
# z=namelistmap()
# ---z---
# z.set( 'zoo', [1, 2, 2, 2] )
# ===direct map==
# zoo --> [1, 2]
# ===reverse map===
# 1 --> ['zoo']
# 2 --> ['zoo']
# =====
# ===direct map==
# foo --> [2, 3, 4]
# bar --> [1, 3, 7]
# ===reverse map===
# 2 --> ['foo']
# 3 --> ['foo', 'bar']
# 4 --> ['foo']
# 1 --> ['bar']
# 7 --> ['bar']
# =====
# x.remove( item=3 )
# ===direct map==
# foo --> [2, 4]
# bar --> [1, 7]
# ===reverse map===
# 2 --> ['foo']
# 4 --> ['foo']
# 1 --> ['bar']
# 7 --> ['bar']
# =====
# >>> 

def default_ambig_solver( l ):
     if(type(l) is not list): 
        raise ValueError
     else:
         if( len(l) == 0 ):
              return None
         else:
              return( l[0] )

class namelistmap( ):
    def __init__( self, inverse_ambiguity_solver = default_ambig_solver ):
        self.itemlistmap = {}
        self.item_to_nm_map = {}
        self.nm_ambig_solver = inverse_ambiguity_solver 
        
    def set( self, nm, itemlist ):
        # the itemlist must not contain duplicate values
        uniq_itemlist = list( set( itemlist )) 
        self.itemlistmap[ nm ] = uniq_itemlist
        for i in uniq_itemlist:
            if i in self.item_to_nm_map.keys():
                if nm not in self.item_to_nm_map[ i ]:
                    self.item_to_nm_map[ i ].append( nm )
            else:
                self.item_to_nm_map[ i ] = [ nm ]

    def add( self, nm, item ):
        if self.get( nm ) is None:
           self.set( nm, [ item ] )
        else:
           self.set( nm, self.itemlistmap[ nm ]  + [ item ] )
                
    def empty( self ):
         return( self.itemlistmap == {} )
 
    def get( self, nm ):
         if nm in self.itemlistmap.keys():
              return( self.itemlistmap[ nm ] )
         else:
              return None

    def get_all_keys( self ):
        return( self.itemlistmap.keys() )

    def get_key_for( self, it ):
         if( it in self.item_to_nm_map.keys() ):
           return( self.nm_ambig_solver( self.item_to_nm_map[ it ] ) )
         else:
           return None
     
    def get_key_list_for( self, it ):
        if( it in self.item_to_nm_map.keys() ):
           return( self.item_to_nm_map[ it ] )
        else:
           return []

    def get_key_list_for_matching_items( self, item_matching_fun = lambda *x : False, item_matching_arglist = [] ):
        matched_key_list = []
        for k in self.get_all_keys():
               if( item_matching_fun( self.itemlistmap[ k ],  *item_matching_arglist )):
                    matched_key_list.append( k )
        return matched_key_list
          
    def remove( self, nm = None, item = None ):
        # NOTE: one span is enough to remove a pattern with several spans, provided it is one of them
        if( nm is not None ):
            assert( item is None )
            for i in self.itemlistmap[ nm ]:
                assert( nm in self.item_to_nm_map[ i ] )
                self.item_to_nm_map[ i ].remove( nm )
            self.itemlistmap.pop( nm )
        else:
            if( item is not None ):
                if( item in self.item_to_nm_map.keys() ):
                     aux_nm_list = []
                     for nm in self.item_to_nm_map[ item ]:
                          self.itemlistmap[ nm ].remove( item )
                          aux_nm_list.append( nm )
                     for n in aux_nm_list:
                          if self.itemlistmap[ n ] is []:
                               self.itemlistmap.remove( n )
                     self.item_to_nm_map.pop( item )
                else:
                    # do nothing the item is not part of the map
                    dummy = None

    def clear( self ):
          self.itemlistmap = {}
          self.item_to_nm_map = {}

    def set_ambig_solver( self, ambg ):
         self.nm_ambig_solver = ambg
                
    def __str__( self ):
         sout = '===direct map==\n'
         for n in self.itemlistmap.keys():
              sout += str( n ) + ' --> ' + str( self.itemlistmap[ n ] ) + '\n'
         sout += '===reverse map===\n'
         all_item_values = []
         # get all the values but only once
         for n in self.itemlistmap.keys():
              for i in self.itemlistmap[ n ]:
                   if i not in all_item_values:
                        all_item_values.append( i )
         for i in all_item_values:
              sout += str(i) + ' --> ' +  str( self.item_to_nm_map[ i ] ) + '\n'
         sout += '====='
         return( sout )

    def __repr__( self ):
         return( '<nm_ambig_solver: ' + str( self.nm_ambig_solver ) + ' itemlistmap: ' + str( self.itemlistmap )  + ' reverse_map: ' + str( self.item_to_nm_map )  + '>' ) 

    def keys_for_item( self, item = None ):
        # given an item it returns the list of names that contain it in their item list
        if( item is not None ):
            if( item in self.item_to_nm_map.keys() ):
                 
                return( self.item_to_nm_map[ item ] )    
            else:
                return( [] )
        else:
            return( [] )

       
