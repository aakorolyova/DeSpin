#! python3
# coding: utf8

import re
import sys
import codecs

from text_span import  document, mwu, rel, relation, construction

# -----
# Frome python documentation on unicode
# >>> u = unichr(40960) + u'abcd' + unichr(1972)   # Assemble a string
# >>> utf8_version = u.encode('utf-8')             # Encode as UTF-8
# >>> type(utf8_version), utf8_version
# (<type 'str'>, '\xea\x80\x80abcd\xde\xb4')
# >>> u2 = utf8_version.decode('utf-8')            # Decode using UTF-8
# >>> u == u2                                      # The two strings match
# True
#----------------------------------------------------------------------------------------
# from https://bugs.python.org/issue7643
# msg97407 - (view) Author: Florent Xicluna (flox) * (Python committer) Date: 2010-01-08 10:32

# Some technical background.

# == Unicode ==

# According to the Unicode Standard Annex #9, a character with
# bidirectional class B is a "Paragraph Separator". And “Because a
# Paragraph Separator breaks lines, there will be at most one per line,
# at the end of that line.”

# As a consequence, there's 3 reasons to identify a character as a
# linebreak:
#  - General Category Zl "Line Separator"
#  - General Category Zp "Paragraph Separator"
#  - Bidirectional Class B "Paragraph Separator"

# There's 8 linebreaks in the current Unicode Database (5.2):
# ------------------------------------------------------------------------
# 000A    LF  LINE FEED                   Cc  B
# 000D    CR  CARRIAGE RETURN             Cc  B
# 001C    FS  INFORMATION SEPARATOR FOUR  Cc  B (UCD 3.1 FILE SEPARATOR)
# 001D    GS  INFORMATION SEPARATOR THREE Cc  B (UCD 3.1 GROUP SEPARATOR)
# 001E    RS  INFORMATION SEPARATOR TWO   Cc  B (UCD 3.1 RECORD SEPARATOR)
# 0085    NEL NEXT LINE                   Cc  B (C1 Control Code)
# 2028    LS  LINE SEPARATOR              Zl  WS  (Unicode)
# 2029    PS  PARAGRAPH SEPARATOR         Zp  B   (Unicode)
# ------------------------------------------------------------------------


# == ASCII ==

# The Standard ASCII control codes (C0) are in the range 00-1F.
# It limits the list to LF, CR, FS, GS, RS.
# Regarding the last three, they are not considered as linebreaks:
# “The separators (File, Group, Record, and Unit: FS, GS, RS and US) were made to
# structure data, usually on a tape, in order to simulate punched cards. End of
# medium (EM) warns that the tape (or whatever) is ending. While many systems use
# CR/LF and TAB for structuring data, it is possible to encounter the separator
# control characters in data that needs to be structured. The separator control
# characters are not overloaded; there is no general use of them except to
# separate data into structured groupings. Their numeric values are contiguous
# with the space character, which can be considered a member of the group, as a
# word separator.”
# (Ref: http://en.wikipedia.org/wiki/Control_character#Data_structuring)

# In conclusion, it may be better to keep things unchanged.
# We may add some words to the documentation for str.splitlines() and bytes.splitlines() to explain what is considered a line break character.

# References:
#  - The Unicode Character Database (UCD): http://www.unicode.org/ucd/
#  - UCD Property Values: http://unicode.org/reports/tr44/#Property_Values
#  - The Bidirectional Algorithm: http://www.unicode.org/reports/tr9/
#  - C0 and C1 Control Codes:
#      http://en.wikipedia.org/wiki/C0_and_C1_control_codes
#-------------------------------------------------------------------------------------

#---character separators---
SPACE = chr(int('0020', 16))
NO_BREAK_SPACE = chr(int('00A0', 16))
OGHAM_SPACE_MARK  = chr(int('1680', 16))
MONGOLIAN_VOWEL_SEPARATOR  = chr(int('180E', 16))
EN_QUAD  = chr(int('2000', 16))
EM_QUAD  = chr(int('2001', 16))
EN_SPACE  = chr(int('2002', 16))
EM_SPACE  = chr(int('2003', 16))
THREE_PER_EM_SPACE  = chr(int('2004', 16))
FOUR_PER_EM_SPACE  = chr(int('2005', 16))
SIX_PER_EM_SPACE  = chr(int('2006', 16))
FIGURE_SPACE  = chr(int('2007', 16))
PUNCTUATION_SPACE  = chr(int('2008', 16))
THIN_SPACE  = chr(int('2009', 16))
HAIR_SPACE  = chr(int('200A', 16))
ZERO_WIDTH_SPACE  = chr(int('200B', 16))
NARROW_NO_BREAK_SPACE  = chr(int('202F', 16))
MEDIUM_MATHEMATICAL_SPACE  = chr(int('205F', 16))
IDEOGRAPHIC_SPACE  = chr(int('3000', 16))
ZERO_WIDTH_NO_BREAK_SPACE  = chr(int('FEFF', 16))
#---line separators---
LINE_FEED = chr(int('000A', 16))
CARRIAGE_RETURN = chr(int('000D', 16))    
INFORMATION_SEPARATOR_FOUR = chr(int('001C', 16))
INFORMATION_SEPARATOR_THREE = chr(int('001D', 16))
INFORMATION_SEPARATOR_TWO = chr(int('001E', 16))
NEL_NEXT_LINE = chr(int('0085', 16))
LINE_SEPARATOR = chr(int('2028', 16))
PARAGRAPH_SEPARATOR = chr(int('2029', 16))

SPC_LST = ( SPACE + 
            NO_BREAK_SPACE + 
            OGHAM_SPACE_MARK  + 
            MONGOLIAN_VOWEL_SEPARATOR + 
            EN_QUAD + 
            EN_QUAD + 
            EM_QUAD +  
            EN_SPACE +  
            EM_SPACE + 
            THREE_PER_EM_SPACE + 
            FOUR_PER_EM_SPACE + 
            SIX_PER_EM_SPACE + 
            FIGURE_SPACE + 
            PUNCTUATION_SPACE + 

            THIN_SPACE + 
            HAIR_SPACE  + 
            ZERO_WIDTH_SPACE + 
            NARROW_NO_BREAK_SPACE + 
            MEDIUM_MATHEMATICAL_SPACE + 
            IDEOGRAPHIC_SPACE + 
            ZERO_WIDTH_NO_BREAK_SPACE +
            LINE_FEED +
            CARRIAGE_RETURN +   
            INFORMATION_SEPARATOR_FOUR +
            INFORMATION_SEPARATOR_THREE +
            INFORMATION_SEPARATOR_TWO +
            NEL_NEXT_LINE +
            LINE_SEPARATOR +
            PARAGRAPH_SEPARATOR )

NON_SPCS = u'[^' + SPC_LST + u']+'
    
class SFRel( object ):
        #---  class variables
        TYPENM='TYPE' # relation annotation aspect/dimension
        TYPE='SameForm' # relation annotation value
        # token tuple indices for: form, span 
        FORM = 0
        SPAN = 1
        # class identifier prefix
        FAMERSUF = 'FAMER_'
        MWUSUF = 'mwu_'
        RELSUF = 'relation_'
        #---
        # Famer = Form SFRel ( SFRel = same + -er suffix)
        def __init__( self ):
            self.doc = None
            # a list of pairs holding the token form and the corresponding span made of the utf8 char offset of the first char and
            # the utf8 char offset after the last character, e.g. self.tokens = [ ( 'the', (0, 3)), ('solution', (4, 12)),...]
            self.tokens = []
            # for each token list the spans of all its occurences, e.g. self.tokspans = { 'the':[ (28, 31), (55, 58), (100,103)], ..., 'hapax':[(240, 243)] ...}
            self.tokspans = {}
            # occurence chains, a dictionary associating to each token defined by a visible character sequence the list of relations linking its occurences in the current document,
            # if the token "the" has 3 occurences defined by the spans: (28, 31), (55, 58), (100, 103)
            # then occ_chains will contain: { 'the':[ <SFRel_1 ..>, <SFRel_2 ..> ] }
            # with SFRel_1.source = (28, 31) and SFRel_1.target = (55, 58)
            #      SFRel_2.source = (55, 58) and SFRel_2.target = (100, 103)
            self.occ_chains = {}
            # the following is a similar data structure for hapax, except that the value part is not a list but a pair, of course.
            self.hapax = {}

        def read( self, path ):
            assert( (type( path ) is str) and (path != '') )
            buffer_sz = 100
            in_strm = codecs.open( path, mode='r', encoding='utf-8', errors='strict', buffering = -1)
            assert( in_strm )
            self.data = u''
            for l in in_strm.readlines( buffer_sz ):
                self.data += l
            in_strm.close()

        def token_split( self ):
            s = 0
            non_spc_patt = re.compile( '[^' + SPC_LST + ']+' )
            spc_only_patt = re.compile( '^[' + SPC_LST + ']+$' )
            while s < len( self.doc.ctnt ):
                res = non_spc_patt.search( self.doc.ctnt, pos=s )
                if( res ):
                    tok = res.group(0)
                    assert( not spc_only_patt.match( tok ) )
                    first,last = res.span(0)
                    assert( type( tok ) is str )
                    self.tokens.append( (tok, (first, last)) )
                    s = last
                else:
                    break

        def token_same_form_rels_file_to_csv( self, in_path, out_path ):
            self.doc = document( ident = in_path, metadata = '' )
            self.doc.read( in_path )
            print( 'done reading' )
            self.token_same_form_rels_text() # Note: annotation result is stored in self.doc as a side effect
            outfile = open( out_path, 'w' )
            outfile.write( '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format( '#n', 'token', 'mwu', 'mwu span #', 'relation type', 'relation target'))
            k = 0
            r = self.doc.rels
            for t in self.tokens:
                container_mwu = self.doc.find_mwu_containing_span( t[ SFRel.SPAN ] )
                if( container_mwu is not None ):
                        container_nm = container_mwu.name
                        container_sz = container_mwu.size()
                else:
                        container_nm  = 'None'
                        container_sz = 0
                container_mwu_idx = 0
                outfile.write( '{0}\t{1}\t{2}\t{3}\t{4}\n'.format( k,
                                                                                  t[ SFRel.FORM ],
                                                                                  t[ SFRel.SPAN ][0],
                                                                                  t[ SFRel.SPAN ][1],
                                                                                  container_nm
                                                                                  ))
                k += 1
            return( self.doc )

        def token_same_form_rels_text( self, in_data = None ):
            # annotate relations between all pairs of token instances having the same form, a token being defined as any sequence of contiguous visible characters
            assert( (type( in_data ) == str) or (in_data is None))
            if( in_data is not None ):
                    self.doc = document( ident = '', content = in_data, metadata = '' )
            self.token_split()
            i = 0; j = 0
            mwn = 0
            reln = 0   
            # the list of created rels (only one direction is stored either source-->target or target-->src in a pair of spans, so when testing a pair of span one must test for the existence of both possible ordering)
            self.tokspans = {} 
            
            for t in self.tokens:
                if t[ SFRel.FORM ] not in self.tokspans:
                    self.tokspans[ t[ SFRel.FORM ] ] = [ t[ SFRel.SPAN ] ]
                else:
                    self.tokspans[ t[ SFRel.FORM ] ].append( t[ SFRel.SPAN ] )

            self.occ_chains = {}
            
            for tok in self.tokspans:
                    self.occ_chains[ tok ] = []
                    if( len( self.tokspans[ tok ] ) > 1 ):
                        for i in range(0, len( self.tokspans[tok ] ) - 1):
                                mw1 = mwu(  nm=(SFRel.FAMERSUF + SFRel.MWUSUF + str(mwn)), txtsps = [ self.tokspans[tok ][i] ] )
                                mwn += 1
                                self.doc.add_mwu( mw1 )
                                mw2 = mwu(  nm=(SFRel.FAMERSUF + SFRel.MWUSUF + str(mwn)), txtsps = [ self.tokspans[tok ][i+1] ] )
                                mwn += 1
                                self.doc.add_mwu( mw2 )
                                new_r = relation(  nm=(SFRel.FAMERSUF + SFRel.RELSUF + str(reln)), src = mw1, trg = mw2 )
                                new_r.set_glob_annot( SFRel.TYPENM, SFRel.TYPE ) 
                                self.doc.add_rel( new_r )
                                self.occ_chains[ tok ].append( new_r )
                                reln += 1
                        assert( len( self.occ_chains[ tok ] ) == (len( self.tokspans[tok ] ) -1) )
                    else:
                        self.hapax[ tok ] = self.tokspans[ tok ][0]
            return( self.doc )

        def make_token_graph( self, out_path ):
                outfile = open( out_path, 'wb' )
                outfile.write( '<BEGINNING>'.encode( 'utf-8' ))
                # make the links over all the occurences chains
                for tok in self.tokens:
                        # NOTE: here tok is the next token
                        # print the next token as the last target of the previous token
                        outfile.write( ' '.encode( 'utf-8' ))
                        outfile.write( '{0}'.format( tok[0] + '_' + str( self.tokspans[tok[0]][0] )).replace( ' ', '').encode( 'utf-8' ))
                        outfile.write( '\n'.encode( 'utf-8' ))
                        # print again the next token as the source of the links towards its other occurences
                        outfile.write( '{0}'.format( tok[0] + '_' + str( self.tokspans[tok[0]][0] )).replace( ' ', '').encode( 'utf-8' ))
                        if( len( self.tokspans[tok[0]] ) > 1):
                                first_occ_span = self.tokspans[tok[0]][0]
                                if( tok[1] == first_occ_span ):
                                        # print the occurence chain of the next token BUT only when encountering the first occurence otherwise we will duplicate the information
                                        # first print a loop on the first occurence itself for a distinguished dipsplay by the drawing function
                                        outfile.write( ' '.encode( 'utf-8' ))
                                        outfile.write( '{0}'.format( tok[0] + '_' + str( self.tokspans[tok[0]][0] )).replace( ' ', '').encode( 'utf-8' ))
                                        # add the links to all the other occurences with the same form
                                        for s in self.tokspans[tok[0]][1:]:
                                                outfile.write( ' '.encode( 'utf-8' ))
                                                outfile.write( '{0}'.format( tok[0] + '_' + str( s )).replace( ' ', '').encode( 'utf-8' ))
                        #NOTE: the last link toward the next token in the document will be printed by the first instruction of the next iteration
                outfile.write( '\n'.encode( 'utf-8' ))
                outfile.close()
                
#end of class SFRel

##DEMO_MODE=True
DEMO_MODE=False                
if DEMO_MODE:
        txt='Our main outcome was a three category asthma variable coded as no asthma (reference category), current asthma, and probable asthma.'
        l=[]
        for w in re.finditer( '[^' + SPC_LST + ']+', txt ):
            l.append( w.group(0) )
        print( l )
        for w in re.finditer( '[^' + SPC_LST + ']+', txt):
            l.append( w.group(0) )
        print( l )
        words = re.split( '[' + SPC_LST + ']+', txt )
        print( words )
        sres = re.search( '^[' + SPC_LST + ']+', txt )
        if sres:
            print( 'search ok' )
            print( '>{0}<'.format( sres.group( 0 ) ) )
        else:
            print( 'nomatch' )
        sres = re.search( '^[' + SPC_LST + ']+', txt[3:] )
        if sres:
            print( 'res ok2' )
            print( '>{0}<'.format( sres.group( 0 ) ) )
        else:
            print( 'nomatch2' )

        print('+++++++++++++++')
        txt='foo bar foo goo foo'
        x=SFRel()
        d = x.token_same_form_rels_text( txt )
        print( 'final result= {0}'.format( d.rels ) )
        for r in d.rels:
                print( r )
                print( r.annotations )
                print( '########' )
                print( r.source )
                print( r.target )
                print( '---================================' )
        print()
        x.make_token_graph( 'foo_graph.txt' )
        print()
        print('________________________')
        x=SFRel()
##        wdir = './'
        wdir=''
        d1 = x.token_same_form_rels_file_to_csv( wdir+'pmc_limsi_1471-2458-5-97.txt', wdir+'pmc_limsi_1471-2458-5-97.sf' )
        print( 'there are {0} token occurences'.format( len(x.tokens) ))
        print( 'there are {0} types with multiple occurences'.format( len(x.occ_chains) ))
        print( 'there are {0} hapax'.format( len(x.hapax) ))
        print( 'created {0} SFRel relations (same form relations linking two subsequent occurences of the same form'.format( len(d1.rels)))
        print( 'occurence chain for \'the\' has length {0}'.format( len(x.occ_chains[ 'the' ])))
        x.make_token_graph( 'pmc_limsi_1471-2458-5-97_graph.txt' )
        x=SFRel()
        d1 = x.token_same_form_rels_file_to_csv(in_path='abstract.txt', out_path='dummy' )
        x.make_token_graph( 'abstract_graph.txt' )




















