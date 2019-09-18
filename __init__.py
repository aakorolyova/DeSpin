#====================
# copyright A. Koroleva and P. Paroubek
# LIMSI-CNRS

from text_span import *
          
# ============= tests ================

#  text initialization 
#with open('/media/pap/HDToshiba1T/work/MIROR/DATA/pmc_limsi_corpus/1471-2458-5-97.txt') as f:
#sample_file_name = 'pmc_limsi_1471-2458-5-97.txt'
#sample_file_name = "1471-2261-6-30.txt"
#sample_file_name = "abstract.txt"
sample_file_name = "DATA/1471-2466-12-69.txt"

with open(sample_file_name) as f:
     text1 = f.read()
print( len( text1 ))
d1 = document( ident=sample_file_name,
               metadata='sample for code testing from pmc limsi corpus from file: '+ sample_file_name,
               content=text1 )
format( 'lenght is {0}', str(d1.len()))

# some sample relation creation

# ======== graphic inteface with TkInter ===========================

from ConstruKT import ConstruKT
app = ConstruKT()
# app.text_init( text=d1.ctnt )
app.document_init( d1 )
app.run()
