#! python3
# coding: utf8

import os
import re
import sys

if sys.version_info[0] != 3:
    print( 'This script requires Python 3' )
    exit()
import codecs
import operator

from namelistmap import namelistmap

from text_span import  mwu, rel, construction, document, relation

from Samer import SFRel

from namespace import namespace

from textfile import textfile, simple_filter_preannot_results, advanced_filter_preannot_results

example = u"""Aspirin increased patient satisfaction. Our primary outcome was the severity of depressive symptoms.
The primary outcome of the randomized controlled trial will include patients' self-reported rates of consideration of LKT ( including family discussions of LKT , patient-physician discussions of LKT , and identification of an LKT donor ) .
Results Biopsy proven acute rejection ( BPAR ) at 24 weeks , the primary study endpoint , was comparable in the L ( 22.8 % ) and MMF ( 17.2 % ) groups but higher in the H ( 34.5 % ) and M ( 29.3 % ) groups .
Results Biopsy proven acute rejection ( BPAR ) , the primary study endpoint , was comparable in the L ( 22.8 % ) and MMF ( 17.2 % ) groups but higher in the H ( 34.5 % ) and M ( 29.3 % ) groups .
Survival, the outcome, .
The mean decrease in the Young Mania Rating Scale score from baseline was used as the main outcome measure of response of mania to treatment .
Primary efficacy measurements were glycemic control and quality of life . 
 """


# converting preannotation format to mwu form

class Annotate( object ):
	def __init__( self, data = None, config_path = None ):
                
		self.config = {} # a dictionary holding attribute value associations for configuring some annotation application, e.g. the treetagger: { 'TREEAGGER_DIR':'/people/koroleva/Desktop/src/TreeTagger'}
		if( config_path is not None ):
			assert(  type( config_path is str ) and os.path.isfile( config_path ) )
			f = open( config_path, 'r' )
			self.config = eval( f.read() )
			f.close()

			# given to namespace, the list of various type names used to build object names (unique identifiers)
			Annotate.SPAN_TYP = 'SPAN'
			Annotate.MWU_TYP = 'MWU'
			Annotate.SRC_TYP = 'SRC'
			Annotate.TRGT_TYP = 'TRGT'
			Annotate.REL_TYP = 'REL'
			Annotate.CONSTRU_TYP = 'CONSTRU'
			Annotate.ALL_TYPS =  [ Annotate.SPAN_TYP, Annotate.MWU_TYP, Annotate.SRC_TYP, Annotate.TRGT_TYP, Annotate.REL_TYP, Annotate.CONSTRU_TYP  ] 
			self.name_mgr = namespace( Annotate.ALL_TYPS )

			self.curr_file = None

			self.data = ''
			self.wn = 0

			if( type( data ) is document ):
				self.doc = data
				self.data = self.doc.ctnt
			else:
				if( type( data ) is str ):
					self.doc = document( ident='', content=data, metadata='')
					self.data = data
				else:
					assert( data is None )
					self.doc = document( ident='', content='', metadata='')
					self.data = data

			self.sentences = []

			self.data_parse = textfile(in_text = self.data, configuration = self.config)

	def read( self, path ):
		self.doc.read( path )

	def detect_text_structure(self):
		# to find title, abstract (results + conclusions), body text when the input is a full text article
		self.data_parse.find_abstract()
		title = self.data_parse.title
		abstract = self.data_parse.abstract
		res = self.data_parse.results
		concl = self.data_parse.conclusions

		cend = 0
		# mwu for title
		if title != None:
			cstart = title[1]
			cend = title[2]
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Title' 
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		if abstract != None:
			cstart = abstract[1]
			cend = abstract[2]
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Abstract' 
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		if res != None:
			cstart = res[1]
			cend = res[2]
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Abstract_Results' 
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		if concl != None:
			cstart = concl[1]
			cend = concl[2]
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Abstract_Conclusions' 
			self.doc.add_mwu( a_mwu )
			self.wn += 1


	def detect_abstract_structure(self):
		# find results and conclusions if the input is an abstract only
		structure = self.data_parse.find_abstr_sections()

		# mwus for beginning of abstract, results, conclusions
		cend = 0
		for item in structure:
			if item != '':
				cstart = self.doc.ctnt.find( item, cend )
				cend = cstart + len( item )
				a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
				if structure.index(item) == 0:
					typ = 'Abstract_beginning'
				elif structure.index(item) == 1:
					typ = 'Abstract_Results'
				elif structure.index(item) == 2:
					typ = 'Abstract_Conclusions'

				a_mwu.typ = typ
				self.doc.add_mwu( a_mwu )
				self.wn += 1


	def split_sentences(self):
		sentences = self.data_parse.sent_split()
		cend = 0
		for sent in sentences:
			cstart = self.doc.ctnt.find( sent, cend )
			cend = cstart + len( sent )
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Sentence'
			self.doc.add_mwu( a_mwu )
			self.wn += 1

			# for convenience of use in other functions
			self.sentences.append((sent, cstart, cend))



	def find_registry_data(self):
		reg_ids = self.data_parse.find_reg_num()
		for reg_id in reg_ids:
			cstart = reg_id[2]	
			cend = reg_id[3]
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = 'Registration_number'
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		self.data_parse.find_web()
		#print(len(self.data_parse.registry_data))

		meta = self.data_parse.parse_all_registries()
		#print(self.data_parse.registry_parsed)
		self.doc.meta = meta


	def find_abbreviations(self):
		abbreviations = self.data_parse.find_abbr()
		if len(abbreviations) > 0:
			for item in abbreviations:
				# full form
				full_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
				self.wn += 1
				full_mwu.typ = 'Full_form'
				self.doc.add_mwu( full_mwu )
				
				# abbreviation
				abbr_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[4], item[5]) ] )
				self.wn += 1
				abbr_mwu.typ = 'Abbreviation'
				self.doc.add_mwu( abbr_mwu )

				abbr_rel = relation( nm='Abbr_rel_' + str(self.wn), src=full_mwu, trg=abbr_mwu, annotations = {}, typ = 'Abbreviation' )
				self.wn += 1
				self.doc.add_rel( abbr_rel )
				


	def preannot_to_mwu( self, preannot_function = '', preann_parser = 'spacy', allow_intersection = False ):
		new_tagging_mwus = []
		function_str = 'self.data_parse.' + preannot_function + '(parser="' + preann_parser + '")' 
		#print(function_str)
		preannotation = eval(function_str)
		#print(preannotation)	

		if allow_intersection == False:
			preannotation_to_import = advanced_filter_preannot_results(preannotation)

		elif allow_intersection == True:
			preannotation_to_import = preannotation


		cend = 0
		for preannot_item in preannotation_to_import:
			typ = preannot_item[0]
			beg = preannot_item[1]
			end = preannot_item[2]
			sent_id = preannot_item[3]
			params = preannot_item[4]

			sent_beg = self.data_parse.sentences[sent_id][1]

			# find start position of the first token, returned by ttagger, plus start position of the sentence
			first_token =  self.data_parse.sentences_tagged[(sent_id, preann_parser)][beg]
			cstart = first_token[3] + sent_beg

			# find end position of the last token, returned by ttagger, plus start position of the sentence
			last_token = self.data_parse.sentences_tagged[(sent_id, preann_parser)][end]
			cend = last_token[4] + sent_beg

			#print(self.data[cstart: cend])
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = typ
			#a_mwu.set_glob_annot( 'Params', params )
			new_tagging_mwus.append( a_mwu )
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		return( new_tagging_mwus )


	def compare_outcomes_abstract_to_body(self):
		print('Start comparing outcomes')
		matching_outcomes, outcomes_not_matched, meta = self.data_parse.compare_po_abstr_bt()
		if len(matching_outcomes) > 0:
			for item in matching_outcomes:
				# PO abstr
				po_abstr_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
				self.wn += 1
				po_abstr_mwu.typ = 'PO'
				self.doc.add_mwu( po_abstr_mwu )
				
				# PO body
				po_bt_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[4], item[5]) ] )
				self.wn += 1
				po_bt_mwu.typ = 'Reported_outcome'
				self.doc.add_mwu( po_bt_mwu )

				out_rel = relation( nm='Out_match_' + str(self.wn), src=po_abstr_mwu, trg=po_bt_mwu, annotations = {}, typ = 'Out_match' )
				self.wn += 1
				self.doc.add_rel( out_rel )

		else:
			self.find_po()

		if len(outcomes_not_matched) > 0:
			for item in outcomes_not_matched:
				# PO
				po_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[1], item[2]) ] )
				self.wn += 1
				po_mwu.typ = 'PO'
				self.doc.add_mwu( po_mwu )

		self.doc.meta = meta


	def compare_po_text_to_registry(self):
		print('Start search for matching outcomes')
		matching_outcomes, outcomes_not_matched, meta = self.data_parse.compare_po_text_registry()

		if len(matching_outcomes) > 0:
			for item in matching_outcomes:
				# PO
				po_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
				self.wn += 1
				po_mwu.typ = 'PO'
				self.doc.add_mwu( po_mwu )

		else:
			self.find_po()

		if len(outcomes_not_matched) > 0:
			for item in outcomes_not_matched:
				# PO
				po_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[1], item[2]) ] )
				self.wn += 1
				po_mwu.typ = 'PO'
				self.doc.add_mwu( po_mwu )

		self.doc.meta = meta


	def find_po(self, preann_parser = 'bert'):
		self.data_parse.find_po(parser = preann_parser)
		po_list = set(self.data_parse.PO_list)

		new_tagging_mwus = []

		for po in po_list:
			typ = 'Out'
			beg = po[2]
			end = po[3]
			sent_id = po[4]
			params = po[5]

			#print(po)
			#print(self.data_parse.sentences)

			sent_beg = self.data_parse.sentences[sent_id][1]
			# find start position of the first token, returned by ttagger, plus start position of the sentence
			first_token =  self.data_parse.sentences_tagged[(sent_id, preann_parser)][beg]
			cstart = first_token[3] + sent_beg

			# find end position of the last token, returned by ttagger, plus start position of the sentence
			last_token = self.data_parse.sentences_tagged[(sent_id, preann_parser)][end]
			cend = last_token[4] + sent_beg
			
			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = typ
			#a_mwu.set_glob_annot( 'Params', params )
			new_tagging_mwus.append( a_mwu )
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		return( new_tagging_mwus )

		
	def find_so(self, preann_parser = 'spacy'):
		self.data_parse.find_po(parser = preann_parser)
		so_list = set(self.data_parse.SO_list)

		new_tagging_mwus = []

		for so in so_list:
			typ = 'Out'
			beg = so[2]
			end = so[3]
			sent_id = so[4]
			params = so[5]

			#print(po)
			#print(self.data_parse.sentences)

			sent_beg = self.data_parse.sentences[sent_id][1]
			# find start position of the first token, returned by ttagger, plus start position of the sentence
			first_token =  self.data_parse.sentences_tagged[(sent_id, preann_parser)][beg]
			cstart = first_token[3] + sent_beg

			# find end position of the last token, returned by ttagger, plus start position of the sentence
			last_token = self.data_parse.sentences_tagged[(sent_id, preann_parser)][end]
			cend = last_token[4] + sent_beg

			a_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (cstart, cend) ] )
			a_mwu.typ = typ
			#a_mwu.set_glob_annot( 'Params', params )
			new_tagging_mwus.append( a_mwu )
			self.doc.add_mwu( a_mwu )
			self.wn += 1

		return( new_tagging_mwus )


	def compare_po_to_reported(self): #, preann_parser = 'bert'):
		print('Start search for matching outcomes')
		matching_outcomes, outcomes_not_matched, meta = self.data_parse.compare_po_rep()
		if len(matching_outcomes) > 0:
			for item in matching_outcomes:
				# PO
				po_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
				self.wn += 1
				po_mwu.typ = 'PO'
				self.doc.add_mwu( po_mwu )
				
				# reported outcome
				out_rep_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[4], item[5]) ] )
				self.wn += 1
				out_rep_mwu.typ = 'Reported_outcome'
				self.doc.add_mwu( out_rep_mwu )

				out_rel = relation( nm='Out_match_' + str(self.wn), src=po_mwu, trg=out_rep_mwu, annotations = {}, typ = 'Out_match' )
				self.wn += 1
				self.doc.add_rel( out_rel )	

		else:
			self.find_po(parser = preann_parser)


		if len(outcomes_not_matched) > 0:
			for item in outcomes_not_matched:
				# PO
				po_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[1], item[2]) ] )
				self.wn += 1
				po_mwu.typ = 'PO'
				self.doc.add_mwu( po_mwu )

		self.doc.meta = meta


	def compare_rep_text_to_registry(self):
		print('Start search for matching outcomes')
		matching_outcomes, meta = self.data_parse.compare_registry_rep()

		if len(matching_outcomes) > 0:
			for item in matching_outcomes:
				# rep
				rep_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
				self.wn += 1
				rep_mwu.typ = 'rep'
				self.doc.add_mwu( rep_mwu )

		else:
			self.data_parse.find_out_rep_abstr()

		self.doc.meta = meta


	def signif_rels(self, preann_parser = 'spacy'):
		print('Start search for outcome-significance pairs')
		out_sig_rels = self.data_parse.find_out_signif_rel_bert()
		for item in out_sig_rels:
			# out
			out_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[2], item[3]) ] )
			self.wn += 1
			out_mwu.typ = 'rep_out'
			self.doc.add_mwu( out_mwu )
				
			# stat
			stat_mwu = mwu( nm = 'mwu_' + str( self.wn ), txtsps = [ (item[4], item[5]) ] )
			self.wn += 1
			stat_mwu.typ = 'Pval'
			self.doc.add_mwu( stat_mwu )

			sig_rel = relation( nm='Sig_rel_' + str(self.wn), src=out_mwu, trg=stat_mwu, annotations = {}, typ = 'out_signif' )
			self.wn += 1
			self.doc.add_rel( sig_rel )	


		
	def import_TandA( self, file ):
		self.all_spans = namelistmap()
		self.all_rels = {}
		self.all_kstructs = {}
		with open(file, mode='r', encoding = 'utf-8') as f:
			file_content = f.read()
			doc_reg = re.compile('document\(.*\)', re.DOTALL| re.IGNORECASE)
			if doc_reg.match(file_content):
				self.doc = eval( file_content )
				self.data = self.doc.ctnt
				self.curr_file = file
				self.data_parse = textfile( in_text = self.data, configuration = self.config)
			else:
				print( 'ERROR tentative to import a text only file!' )             
               
	def import_Tonly( self, file ):
		if( (file != None) and (file != '') and (file != ()) ):
			self.all_spans = namelistmap()
			self.all_rels = {}
			self.all_kstructs = {}
			with open(file, mode='r', encoding = 'utf-8') as f:
				file_content = f.read()
				file_ident = str(file)
				self.doc = document(ident = file_ident, content = file_content)
				self.data = self.doc.ctnt
				self.curr_file = file
				self.data_parse = textfile( in_text = self.data, configuration = self.config)



	def python_export( self, file  ):
		with open( file, mode='w+', encoding = 'utf-8') as f:
			f.write( 'document( ident=' + file.__repr__() + ',  content=' + self.doc.content().__repr__() + ', metadata=' + self.doc.meta.__repr__() + ', multi_word_units =' )
			f.write( '[' )
			n = 0
			mwul = []
			for m in self.doc.mwus:
				if( n > 0 ):
					f.write( ', ' )
				f.write( 'mwu( nm=\'' + m.name + '\', txtsps=[ ' )
				n += 1
				sp_lst = []
				len_all_spans = len(m.txtspans)
				span_count = 0
				for sp in m.txtspans:
					f.write( '(' + str( sp[0] ) + ' , ' + str( sp[1] ) + ')' )
					span_count += 1
					if span_count < len_all_spans:
						f.write(',')   
					sp_lst += [ (sp[0], sp[1]) ]   
				mwul += [ mwu( nm = m.name , txtsps = sp_lst) ]
				# [ mwu( nm='FAMER_mwu_0', txtsps=[(16, 19)]), ...
				f.write( '])' )
			f.write( '], ')
			f.write( 'relations= [' )
			n = 0
			for r in self.doc.rels:
				if( n > 0 ):
					f.write( ', ' )
				f.write( '{0}'.format( r.__repr__() ))
				n += 1
			f.write( '], constructions= [' )
			n = 0
			for k in self.doc.kstructs:
				if( n > 0 ):
					f.write( ', ' )
				f.write( '{0}'.format( k.__repr__() ))
				n += 1
			f.write( '])' )
			f.close()

	def export_TandA( self, file ):
		if( (file != None) and (file != '') and (file != ())):
			self.python_export( file )
			self.curr_file = file

	def export_Tonly( self, file ):
		if( (file != None) and (file != '') and (file != ())):
			outf = open( file, 'w' )
			outf.write( self.doc.content() )
			outf.close()
			self.curr_file = file

	def generate_report(self):
		report = self.data_parse.generate_report()
		return report

"""
example_annotate = Annotate(data = example)
mwus_preannot = example_annotate.preannot_to_mwu( preannot_function = 'preannot_po()', allow_intersection = False )
print(mwus_preannot)
print(example_annotate.doc.mwus)


mwus_preannot = example_annotate.preannot_to_mwu( preannot_function = 'preannot_reported_outcomes()', allow_intersection = False )
print(mwus_preannot)
print(example_annotate.doc.mwus)
"""
##ex=0
##a = Annotate( data = 'foo\nbar zoo\ngoo too', config_path = 'pap_pc_construkt.cfg' )
##print( a.data)
##print('{0}---------------------------------'.format( ex )); ex += 1
##d=document(ident='1471-2261-6-30.txt')
##d.read('DATA/1471-2261-6-30.txt')    
##a = Annotate( data = d, config_path = 'pap_pc_construkt.cfg' )
##print( a.data)
##print('{0}---------------------------------'.format( ex )); ex += 1  
##a = Annotate( data='', config_path = 'pap_pc_construkt.cfg' )
##a.import_Tonly( 'DATA/1471-2261-6-30.txt' )
##print( a.data )
##print('{0}---------------------------------'.format( ex )); ex += 1 
##a.export_Tonly( 'DATA/1471-2261-6-30_copy.txt')
##b = Annotate( data='', config_path = 'pap_pc_construkt.cfg' )
##b.import_Tonly( 'DATA/1471-2261-6-30_copy.txt' )
##print( b.data )
##print('{0}---------------------------------'.format( ex )); ex += 1 
##a = Annotate( data='',  config_path = 'pap_pc_construkt.cfg' )
##a.import_TandA( 'DATA/OUTPUT/1465-9921-8-45.txt' ) 
##print( a.doc )
##a.export_TandA( 'DATA/OUTPUT/1465-9921-8-45_copy.txt')
##b = Annotate( data='', config_path = 'pap_pc_construkt.cfg' )
##b.import_TandA( 'DATA/OUTPUT/1465-9921-8-45_copy.txt' )
##print( b )
##print('{0}---------------------------------'.format( ex )); ex += 1 
