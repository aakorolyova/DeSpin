# -*- coding: utf-8 -*-

import os
import codecs
import ntpath
import re
import operator
from nltk.tokenize import sent_tokenize
import operator
from parse_registry import *
import urllib.request

import nltk 
import numpy as np

# bert ner
from bert_master import run_classifier
from biobert_master import run_re, run_ner
from biobert_master.biocodes import ner_detokenize
from biobert_master.tokenization import BasicTokenizer

import tensorflow as tf
flags = tf.flags
FLAGS = flags.FLAGS

depparser = 'spacy'
import spacy
nlp_spacy = spacy.load('en_core_web_sm')
from spacy.cli import convert
from spacy.tokens import Doc
from spacy.vocab import Vocab
	
def spacy_tok_index(span):
	indices = []
	for token in span:
		indices.append(token.i)
		
	indices = sorted(indices)
	return indices
	
def spacy_tok_offset(doc):
	tend = 0
	tok_offset = {}
	for token in doc:
		#print(token.text, token.pos_, token.tag_, token.i, token.lemma_, token.dep_)
		tstart = doc.text.find( token.text, tend )
		if tstart == -1:
			print(token, tend)
			print('Warning: token string not found')
		else:
			tend = tstart + len( token )
			
		tok_offset[token.i] = (tstart, tend)	
	return tok_offset	


DEBUG = False

def check_token(tok_num, tagged, token_list = [], pos_list = [], lemma_list = [], token_not_list = [], pos_not_list = [], lemma_not_list = [], mode_pos='OR', reg = False, casesens = False):
	if tok_num < len(tagged):
		item = tagged[tok_num]
		token = item[0]
		pos = item[1]
		lemma = item[2].lower()

		check_tok = 0
		check_pos = 0
		check_lemma = 0
		check_not_tok = 0
		check_not_pos = 0
		check_not_lemma = 0

		# positive conditions
		if token_list == []:
			if mode_pos=='AND': check_tok = 1
		elif reg == False and casesens == False and token.lower() in token_list:
			check_tok = 1
		elif reg == False and casesens == True and token in token_list:
			check_tok = 1
		elif reg == True and casesens == False:
			pattern = re.compile(token_list[0], re.IGNORECASE)
			if re.search(pattern, token):
				check_tok = 1
		elif reg == True and casesens == True:
			pattern = re.compile(token_list[0])
			if re.search(pattern, token):
				check_tok = 1

		if pos_list == []:
			if mode_pos=='AND': check_pos = 1
		elif reg == False and pos in pos_list:
			check_pos = 1
		elif reg == True:
			pattern = re.compile(pos_list[0])
			if re.search(pattern, pos):
				check_pos = 1

		if lemma_list == []:
			if mode_pos=='AND': check_lemma = 1
		elif reg == False and lemma in lemma_list:
			check_lemma = 1
		elif reg == True:
			pattern = re.compile(lemma_list[0])
			if re.search(pattern, lemma):
				check_lemma = 1


		# negative conditions
		if token_not_list == []:
			check_not_tok = 1
		elif token not in token_not_list:
			check_not_tok = 1
	
		if pos_not_list == []:
			check_not_pos = 1
		elif pos not in pos_not_list:
			check_not_pos = 1
	
		if lemma_not_list == []:
			check_not_lemma = 1
		elif lemma not in lemma_not_list:
			check_not_lemma = 1

		if mode_pos=='OR':
			if (check_tok == 1 or check_pos == 1 or check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False
		elif mode_pos=='AND':
			if (check_tok == 1 and check_pos == 1 and check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False
	else:
		return False


def check_right(tok_num, tagged, token_list = [], pos_list = [], lemma_list = [], token_not_list = [], pos_not_list = [], lemma_not_list = [], mode_pos='OR', reg = False, casesens = False):
	i = tok_num + 1
	if i < len(tagged):	
		next = tagged[i]
		token_next = next[0]
		pos_next = next[1]
		lemma_next = next[2].lower()

		check_tok = 0
		check_pos = 0
		check_lemma = 0
		check_not_tok = 0
		check_not_pos = 0
		check_not_lemma = 0


		#positive conditions
		if token_list == []:
			if mode_pos=='AND': check_tok = 1
		elif reg == False and casesens == False and token_next.lower() in token_list:
			check_tok = 1
		elif reg == False and casesens == True and token_next in token_list:
			check_tok = 1
		elif reg == True and casesens == False:
			pattern = re.compile(token_list[0], re.IGNORECASE)
			if re.search(pattern, token_next):
				check_tok = 1
		elif reg == True and casesens == True:
			pattern = re.compile(token_list[0])
			if re.search(pattern, token_next):
				check_tok = 1

		if pos_list == []:
			if mode_pos=='AND': check_pos = 1
		elif reg == False and pos_next in pos_list:
			check_pos = 1
		elif reg == True:
			pattern = re.compile(pos_list[0])
			if re.search(pattern, pos_next):
				check_pos = 1

		if lemma_list == []:
			if mode_pos=='AND': check_lemma = 1
		elif reg == False and lemma_next in lemma_list:
			check_lemma = 1
		elif reg == True:
			pattern = re.compile(lemma_list[0])
			if re.search(pattern, lemma_next):
				check_lemma = 1

		# negative conditions
		if token_not_list == []:
			check_not_tok = 1
		elif token_next not in token_not_list:
			check_not_tok = 1
	
		if pos_not_list == []:
			check_not_pos = 1
		elif pos_next not in pos_not_list:
			check_not_pos = 1
		
		if lemma_not_list == []:
			check_not_lemma = 1
		elif lemma_next not in lemma_not_list:
			check_not_lemma = 1
		

		if mode_pos=='OR':
			if (check_tok == 1 or check_pos == 1 or check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False
		elif mode_pos=='AND':
			if (check_tok == 1 and check_pos == 1 and check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False
	else:
		return False

def check_left(tok_num, tagged, token_list = [], pos_list = [], lemma_list = [], token_not_list = [], pos_not_list = [], lemma_not_list = [], mode_pos='OR', reg = False, casesens = False):
	i = tok_num - 1
	if i >= 0:	
		prev = tagged[i]
		token_prev = prev[0]
		pos_prev = prev[1]
		lemma_prev = prev[2].lower()

		check_tok = 0
		check_pos = 0
		check_lemma = 0
		check_not_tok = 0
		check_not_pos = 0
		check_not_lemma = 0
	

		#positive conditions
		if token_list == []:
			if mode_pos=='AND': check_tok = 1
		elif reg == False and casesens == False and token_prev.lower() in token_list:
			check_tok = 1
		elif reg == False and casesens == True and token_prev in token_list:
			check_tok = 1
		elif reg == True and casesens == False:
			pattern = re.compile(token_list[0], re.IGNORECASE)
			if re.search(pattern, token_prev):
				check_tok = 1
		elif reg == True and casesens == True:
			pattern = re.compile(token_list[0])
			if re.search(pattern, token_prev):
				check_tok = 1

		if pos_list == []:
			if mode_pos=='AND': check_pos = 1
		elif reg == False and pos_prev in pos_list:
			check_pos = 1
		elif reg == True:
			pattern = re.compile(pos_list[0])
			if re.search(pattern, pos_prev):
				check_pos = 1

		if lemma_list == []:
			if mode_pos=='AND': check_lemma = 1
		elif reg == False and lemma_prev in lemma_list:
			check_lemma = 1
		elif reg == True:
			pattern = re.compile(lemma_list[0])
			if re.search(pattern, lemma_prev):
				check_lemma = 1

		# negative conditions
		if token_not_list == []:
			check_not_tok = 1
		elif token_prev not in token_not_list:
			check_not_tok = 1

		if pos_not_list == []:
			check_not_pos = 1
		elif pos_prev not in pos_not_list:
			check_not_pos = 1

		if lemma_not_list == []:
			check_not_lemma = 1
		elif lemma_prev not in lemma_not_list:
			check_not_lemma = 1

		if mode_pos=='OR':
			if (check_tok == 1 or check_pos == 1 or check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False
		elif mode_pos=='AND':
			if (check_tok == 1 and check_pos == 1 and check_lemma == 1) and (check_not_tok == 1 and check_not_pos == 1 and check_not_lemma == 1):
				return True
			else:
				return False

	else:
		return False


def check_right_group(tok_num, group):
	beg = group[0]
	end = group[1]
	if beg == tok_num + 1:
		return True
	else:
		return False


def check_left_group(tok_num, group):
	beg = group[0]
	end = group[1]
	if end == tok_num - 1:
		return True
	else:
		return False


# a class that includes all the possible operations that we may want to do with a text
# Input is a path to text of just a source text (not allowed to enter both types of input together).
# Operations:
# treetag
# custom tokenisation
# search for trial registration number
# download data from the registry website, given the registration number
# parse the downloaded data to get certain types of information
# pre-anotate the text for entities and certain constructions
class textfile:

	def __init__(self, in_path = '', in_text = '', configuration = {} ):
		# a dictionary holding attribute value associations for configuring some annotation application, e.g. the treetagger: { 'TREEAGGER_DIR':'/people/koroleva/Desktop/src/TreeTagger'}
		self.config = configuration
		if in_path == '' and in_text == '':
			self.text = ''
		elif in_path != '' and in_text != '':
			print("You should give either a path or a text as an input; both are not allowed.")
		elif in_path != '' and in_text == '':
			self.path = in_path
			fileopen = codecs.open(in_path, 'r', encoding = 'utf-8')
			self.text = fileopen.read()
			if len(self.text) == 0: print("Text is empty.")
			fileopen.close()
		elif in_text != '' and in_path == '':
			self.text = in_text


		self.text = re.sub("\r\n", "\n", self.text)
				
		self.text_to_process = self.text

		self.sentences = []
		self.tokens = []
		self.tags = []
		self.name = ntpath.basename(in_path)
		self.dir = os.path.dirname(in_path)
		self.ext = os.path.splitext(in_path)[1]

		self.tags_offset = []
		self.spaces = []

		self.pre_annot = ""
		self.text_ac = ""


		self.glozz_converted = ""

		self.sentences_tagged = {}
		self.sentences_depparsed = {}
		self.chunks_spacy = set()
		#self.sentences_bert_tokenized = {}
		
		self.annotations = []

		self.ids = None
		self.registry_data = None
		self.registry_parsed = None

		self.abbreviations = None
		self.abbr_dict = None

		self.NPs = {}

		self.outcomes_declared = None
		self.outcomes_reported = None

		self.PO_list = None
		self.PO_abstr_list = None
		self.PO_bt_list = None
		self.out_rep_abstr = None
		self.out_measures = None

		self.stats = None

		self.title = None
		self.abstract = None
		self.body = None

		self.results = None
		self.conclusions = None          

        
	def sent_split(self):
		# sentence splitter from NLTK
		sentences = sent_tokenize(self.text)

		sentences_with_positions = []
		sent_end = 0
		for sent in sentences:
			sent_beg = self.text.find(sent, sent_end)
			sent_end = sent_beg + len(sent)
			sentences_with_positions.append((sent, sent_beg, sent_end))

		self.sentences = sentences_with_positions
		return self.sentences

	def bert_tokenize_sent(self, do_lower = False, sentence = ''):
		bert_tokenizer = BasicTokenizer(do_lower_case = do_lower)
		sent_toks = bert_tokenizer.tokenize(sentence)

		toks_with_positinos = []
		tend = 0
		for tok in sent_toks:
			if do_lower:
				tstart = sentence.lower().find( tok, tend )
			else:
				tstart = sentence.find( tok, tend )
			if tstart == -1:
				print(tok, tend)
				print('Warning: token string not found!')
			else:
				tend = tstart + len( tok )
			toks_with_positinos.append((tok, '', '', tstart, tend))

		return(toks_with_positinos)

	def depparse_sent(self, depparser = '', sentence = ''):
		if depparser == 'spacy':
			sent_tagged = nlp_spacy(sentence)
			#for token in sent_tagged:
			#	print(token.i, token, token.pos_, token.lemma_, token.head, token.tag_, token.dep_)
		elif depparser == 'stanfordcorenlp':
			sent_tagged = conll_to_graph(in_text = stanford_to_conll(sentence))
		elif depparser == 'malt':
			sent_tagged = conll_to_graph(in_text = malt_to_conll(sentence))
		elif depparser == 'bllipparser':
			sent_tagged = conll_to_graph(in_text = bllipparser_to_conll(sentence))
		tend = 0
		tags_with_positions = []
		deptags_with_positions = []

		for item in sent_tagged:
			token = item.text
			tag = item.tag_
			lemma = item.lemma_

			tstart = sentence.find( token, tend )
			if tstart == -1:
				print(token, tend)
				print('Warning: token string not found!')
			else:
				tend = tstart + len( token )
			tags_with_positions.append((token, tag, lemma, tstart, tend))
			#print(token, tstart, tend)
			deptags_with_positions.append((item, tstart, tend))

		if depparser == 'spacy':
			for chunk in sent_tagged.noun_chunks:
				tok_beg = chunk.start
				tok_end = chunk.end - 1
				tok_beg_pos = tags_with_positions[tok_beg][3]
				tok_end_pos = tags_with_positions[tok_end][4] - 1
				self.chunks_spacy.add((sentence[tok_beg_pos: tok_end_pos + 1], tok_beg_pos, tok_end_pos))

		return tags_with_positions, deptags_with_positions


	def find_reg_num(self):
		# find the trial registration number(s), return a tuple of registry name + number
		registr_reg = re.compile("(trial registe?r(ation|y|d)?|(registration|clinical|register|study|trial) number|(is|was|been) registered|identifier|\\bID\\b|\\b(?:NCT|ACTR|ANZCTR|ISRCT|ISRTC|ISCT|ISCRT|NTR|RBR|ChiCTR|DRKS|UMIN|EudraCT|EUCTR|PACTR|KCT|IRCT|CTRI|RPCEC|SLCTR))", re.IGNORECASE)

		#ID_reg = re.compile("\\b(NCT|ACTRN?|ANZCTRN?|ISRCTN?|ISRTCN?|ISCTN?|ISCRTN?|NTR|TC|RBR|ChiCTR-[A-Z]+|DRKS|UMIN|EudraCT|EUCTR|PACTR|KCT|IRCT|CTRI|RPCEC|SLCTR)(?:[# =:\(\)-]|numbers?|no\.?|n°|№)*([0-9N/][A-Z0-9/-]+[0-9])", re.IGNORECASE)

		ID_reg = re.compile("\\b(NCT|ACTRN?|ANZCTRN?|ISRCTN?|ISRTCN?|ISCTN?|ISCRTN?|NTR|TC|RBR|ChiCTR-[A-Z]+|DRKS|UMIN|EudraCT|EUCTR|PACTR|KCT|IRCT|CTRI|RPCEC|SLCTR)(?:[# =:\(\)-]|numbers?|no\.?|n°|№|/pf/)*(?:\\1)?([0-9N/][A-Z0-9/-]+[0-9])", re.IGNORECASE)

		num_reg = re.compile("([0-9N/][A-Z0-9/-]+)")

		text = self.text
		parags = text.split("\n")
    
		ids = set()
		for parag in parags:
			registr = registr_reg.search(parag)
			if registr:
				for match in ID_reg.finditer(parag):
					registry = match.group(1)
					num = str(match.group(2))
					if registry.lower() == "tc":
						if abs(registr.start() - match.start()) <= 50:
							ids.add((registry, num, match.start(), match.end()))
					else:
						ids.add((registry, num, match.start(), match.end()))

		self.ids = ids
		return ids


	def find_web(self):
		# take trial registration number, go to the website of the registry and try to download the trial data
		if self.ids == None:
			self.find_reg_num()
		self.registry_data = set()

		if len(self.ids) == 0:
			print("No registration number found.")	

		for id in self.ids:
			registry = id[0]
			num = id[1]
			fullnum = registry + num
##			print(fullnum)
			registry = registry.lower()

			if (registry.find("actr") is not -1) or (registry.find("anzctr") is not -1):
				registry_new = "actrn"
			elif (registry.find("isrct") is not -1) or (registry.find("isrtcn") is not -1) or (registry.find("isct") is not -1) or (registry.find("iscrt") is not -1):
				registry_new = "isrctn"
			elif registry == "umin":
				registry_new = "JPRN-UMIN"
			elif registry == "eudract":
				registry_new = "euctr"
			else:
				registry_new = registry

			info = ''

			try:
				#who_search = urllib.request.urlopen("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + registry_new + num)
				#print("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + registry_new + num)
				#search = who_search.read()
				who_search = urllib.request.urlopen("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + registry_new + num).read().decode()
				self.registry_data.add(("who", num, who_search))
				if who_search != '':
					address = re.search("URL:.*?href=\"([^\"]+)", who_search, flags=re.DOTALL)
					if address:
						pagename = address.group(1)
						pagename = pagename.replace("&amp;", "&")
						web = urllib.request.urlopen(pagename)
						info = web.read().decode()
						#info = urlread(pagename)
						
						if info != '':
							self.registry_data.add((registry, num, info))

			except Exception as e:
				print('who', registry, e)

			if info=='':
				if registry == "nct":
					try:
						web = urllib.request.urlopen("https://clinicaltrials.gov/ct2/show/" + fullnum)
						info = web.read().decode()
						#info = urlread("https://clinicaltrials.gov/ct2/show/" + fullnum)
					except Exception as e:
						print(registry, e)

				elif registry == "pactr":
					try:
						web = urllib.request.urlopen("http://www.pactr.org/ATMWeb/appmanager/atm/atmregistry?dar=true&tNo=" + fullnum)
						info = web.read().decode()
						#info = urlread("http://www.pactr.org/ATMWeb/appmanager/atm/atmregistry?dar=true&tNo=" + fullnum)
					except Exception as e:
						print(registry, e)

				elif registry == "ntr" or registry == "tc":
					if len(num) < 6 and len(num) >= 4:
						try:
							web = urllib.request.urlopen("http://www.trialregister.nl/trialreg/admin/rctview.asp?TC=" + num)
							info = web.read().decode()
							#info = urlread("http://www.trialregister.nl/trialreg/admin/rctview.asp?TC=" + num)
						except Exception as e:
							print(registry, e)

				elif registry == "rbr":
					try:
						web = urllib.request.urlopen("http://www.ensaiosclinicos.gov.br/rg/" + registry + "-" + num + "/")
						info = web.read().decode()
						#info = urlread("http://www.ensaiosclinicos.gov.br/rg/" + registry + "-" + num + "/")
					except Exception as e:
						print(registry, e)

				elif registry.find("chictr") is not -1:
					try:
						search = urllib.request.urlopen("http://www.chictr.org.cn/searchprojen.aspx?title=&officialname=&subjectid=&secondaryid=&applier=&studyleader=&ethicalcommitteesanction=&sponsor=&studyailment=&studyailmentcode=&studytype=0&studystage=0&studydesign=0&minstudyexecutetime=&maxstudyexecutetime=&recruitmentstatus=0&gender=0&agreetosign=&secsponsor=&regno=" + registry + "-" + num + "&regstatus=0&country=&province=&city=&institution=&institutionlevel=&measure=&intercode=&sourceofspends=&createyear=0&isuploadrf=&whetherpublic=&btngo=btn&page=1")
						search = search.read().decode()
						#search = urlread("http://www.chictr.org.cn/searchprojen.aspx?title=&officialname=&subjectid=&secondaryid=&applier=&studyleader=&ethicalcommitteesanction=&sponsor=&studyailment=&studyailmentcode=&studytype=0&studystage=0&studydesign=0&minstudyexecutetime=&maxstudyexecutetime=&recruitmentstatus=0&gender=0&agreetosign=&secsponsor=&regno=" + registry + "-" + num + "&regstatus=0&country=&province=&city=&institution=&institutionlevel=&measure=&intercode=&sourceofspends=&createyear=0&isuploadrf=&whetherpublic=&btngo=btn&page=1")

						page = re.search("<a href=\"(showprojen\.aspx\?proj=\d+)\">", search)
						if page:
							pagename = page.group(1)
							web = urllib.request.urlopen("http://www.chictr.org.cn/" + pagename)
							info = web.read().decode()
							#info = urlread("http://www.chictr.org.cn/" + pagename)
					except Exception as e:
						print(registry, e)

				elif registry == "drks":
					try:
						web = urllib.request.urlopen("http://drks-neu.uniklinik-freiburg.de/drks_web/navigate.do?navigationId=trial.HTML&TRIAL_ID=" + fullnum)
						info = web.read().decode()
						#info = urlread("http://drks-neu.uniklinik-freiburg.de/drks_web/navigate.do?navigationId=trial.HTML&TRIAL_ID=" + fullnum)
					except Exception as e:
						print(registry, e)

				elif registry == "eudract" or registry == "euctr":
					num = num.replace("-", "")
					#print(num)
					num_div = re.search("(\d{4})(\d{6})(\d{2})", num)
					if num_div:
						num_split = str(num_div.group(1)) + "-" + str(num_div.group(2)) + "-" + str(num_div.group(3))
						try:
							web = urllib.request.urlopen("https://www.clinicaltrialsregister.eu/ctr-search/search?query=" + num_split)
							info = web.read().decode()
							#info = urlread("https://www.clinicaltrialsregister.eu/ctr-search/search?query=" + num_split)

							protocol_reg = re.compile("<span class=\"label\">Trial protocol:</span>.*?<a href=\"(.*?)\">", re.DOTALL | re.IGNORECASE)
							protocol = protocol_reg.search(info)
							if protocol:
								protocol = protocol.group(1)
								web_pr = urllib.request.urlopen("https://www.clinicaltrialsregister.eu" + protocol)
								info_pr = web_pr.read().decode()
	 
								if info_pr != '':
									self.registry_data.add(('eudract_protocol', num, info_pr))
		 
						except Exception as e:
							print(registry, e)

				elif registry == "irct":
					try:
						search = urllib.request.urlopen("http://en.search.irct.ir/search?query=" + fullnum)
						search = search.read().decode()
						#search = urlread("http://en.search.irct.ir/search?query=" + fullnum)

						page = re.search("<a href=\"(/view/\d+)\">", search)
						if page:
							pagename = page.group(1)
##							print(pagename)
							web = urllib.request.urlopen("http://en.search.irct.ir" + pagename)
							info = web.read().decode()
							#info = urlread("http://en.search.irct.ir" + pagename)
					except Exception as e:
						print(registry, e)

				elif registry == "ctri":
					try:
						web = urllib.request.urlopen("http://ctri.nic.in/Clinicaltrials/showallp.php?mid1=365&EncHid=&userName=" + fullnum)
						info = web.read().decode()
						#info = urlread("http://ctri.nic.in/Clinicaltrials/showallp.php?mid1=365&EncHid=&userName=" + fullnum)
					except Exception as e:
						print(registry, e)

				elif registry == "rpcec":
					try:
						web = urllib.request.urlopen("http://registroclinico.sld.cu/ensayos/" + fullnum + "-Sp")
						info = web.read().decode()
						#info = urlread("http://registroclinico.sld.cu/ensayos/" + fullnum + "-Sp")
					except Exception as e:
						print(registry, e)


				elif (registry.find("actr") is not -1) or (registry.find("anzctr") is not -1):
					try:
						web = urllib.request.urlopen("http://www.anzctr.org.au/TrialSearch.aspx?searchTxt=" + "actrn" + num + "&isBasic=True")
						search = web.read().decode()
						#search = urlread("http://www.anzctr.org.au/TrialSearch.aspx?searchTxt=" + "actrn" + num + "&isBasic=True")

						page = re.search("href=\"(\S+?)\">View full record</a>", search)
						if page:
							pagename = page.group(1)
							info = urllib.request.urlopen("https://www.anzctr.org.au/" + pagename).read().decode()

					except Exception as e:
						print(registry, e)

				elif (registry.find("isrct") is not -1) or (registry.find("isrtcn") is not -1) or (registry.find("isct") is not -1) or (registry.find("iscrt") is not -1):
					try:
						web = urllib.request.urlopen("https://www.isrctn.com/" + "ISRCTN" + num + "?q=" + num + "&filters=&sort=&offset=1&totalResults=1&page=1&pageSize=10&searchType=basic-search")
						info = web.read().decode()	
						#info = urlread("https://www.isrctn.com/" + "ISRCTN" + num + "?q=" + num + "&filters=&sort=&offset=1&totalResults=1&page=1&pageSize=10&searchType=basic-search")
					except Exception as e:
						print(registry, e)

				elif registry == "umin":
					try:
						web = urllib.request.urlopen("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + "JPRN-" + fullnum)
						info = web.read().decode()
						#info = urlread("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + "JPRN-" + fullnum)
					except Exception as e:
						print(registry, e)

				elif registry == "kct" or registry=="slctr":
					try:
						web = urllib.request.urlopen("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + fullnum)
						info = web.read().decode()
						#info = urlread("http://apps.who.int/trialsearch/Trial2.aspx?TrialID=" + fullnum)
					except Exception as e:
						print(registry, e)


				if info != '':
					self.registry_data.add((registry, num, info))

				#else:
					#print(filename)


	def parse_all_registries(self):
		parse_results = set()
		self.registry_parsed = set()
		if self.registry_data == None:
			self.find_web()

		if len(self.registry_data) == 0:
			print("No registry entry found")

		meta = ''
		if DEBUG: print(self.registry_data)
		for registry_entry in self.registry_data:
			registry = registry_entry[0]
			reg_num = registry_entry[1]
			registry_data = registry_entry[2]
			parse_results = eval('parse_' + registry + '(registry_data)')
			self.registry_parsed.add((registry, reg_num, str(parse_results)))
			for item in parse_results.keys():
				meta += item
				for val in parse_results[item]:
					meta += '\t' + val
				meta += '\n'		

		if DEBUG: print(self.registry_parsed)
		return meta


	def replace_numerals(self):
		text = self.text
		text = re.sub('\\bone\\b', '1', text)
		text = re.sub('\\btwo\\b', '2', text)
		text = re.sub('\\bthree\\b', '3', text)
		text = re.sub('\\bfour\\b', '4', text)
		text = re.sub('\\bfive\\b', '5', text)
		text = re.sub('\\bsix\\b', '6', text)
		text = re.sub('\\bseven\\b', '7', text)
		text = re.sub('\\beight\\b', '8', text)
		text = re.sub('\\bnine\\b', '9', text)
		text = re.sub('\\bten\\b', '10', text)
		text = re.sub('\\beleven\\b', '11', text)
		text = re.sub('\\btwelve\\b', '12', text)
		text = re.sub('\\bthirteen\\b', '13', text)
		text = re.sub('\\bfourteen\\b', '14', text)
		text = re.sub('\\bfifteen\\b', '15', text)
		text = re.sub('\\bsixteen\\b', '16', text)
		text = re.sub('\\bseventeen\\b', '17', text)
		text = re.sub('\\beighteen\\b', '18', text)
		text = re.sub('\\bnineteen\\b', '19', text)
		text = re.sub('\\btwenty\\b', '20', text)
		text = re.sub('\\bthirty\\b', '30', text)
		text = re.sub('\\bforty\\b', '40', text)
		text = re.sub('\\bfifty\\b', '50', text)
		text = re.sub('\\bsixty\\b', '60', text)
		text = re.sub('\\bseventy\\b', '70', text)
		text = re.sub('\\beighty\\b', '80', text)
		text = re.sub('\\bninety\\b', '90', text)
		text = re.sub('\\bhundred\\b', '100', text)
		text = re.sub('\\bthousand\\b', '1000', text)
		
		big_num_reg = re.compile('(\d+) (1000?)')
		for match in big_num_reg.finditer(text):
			num1 = match.group(1)
			num2 = match.group(2)
			new_num = int(num1) * int(num2)
			
			text = re.sub(match.group(0), str(new_num), text)
			
		num_seq_reg = re.compile('(\d+)[ -](\d+)')
		for match in num_seq_reg.finditer(text):
			num1 = match.group(1)
			num2 = match.group(2)
			new_num = int(num1) + int(num2)
			
			text = re.sub(match.group(0), str(new_num), text)		
			
		return text	


	def find_abbr(self):
		abbr_reg = re.compile("\(\s*([a-z-]{2,})\s*\)", re.IGNORECASE)
		abbr_num_reg = re.compile("\(\s*([a-z-]{2,})[ -]?([0-9iv]+)\s*\)", re.IGNORECASE)

		abbr_reg_no_brackets = re.compile("\s*([a-z-]{2,})\s*", re.IGNORECASE)
		abbr_num_reg_no_brackets = re.compile("\s*([a-z-]{2,})[ -]?([0-9iv]+)\s*", re.IGNORECASE)

		abbr_list = set()

		text = self.replace_numerals()
		#text = re.sub("\n", " ", text)

		abbr_set = set()

		for abbr_match in abbr_reg.finditer(text):
			abbr = abbr_match.group(0)
			symbols = re.findall("\w", abbr)
            
			pattern = "\\b"
			for i in range(0, len(symbols)):
				pattern = pattern + symbols[i] + "[a-z-]*?[\s-]+(?:[a-z]{1,3}[\s-]+)?"
            
			pattern = "(" + pattern + ")" + "\(\s*" + "(" + abbr + ")" + "\s*\)"
			#print(abbr, symbols, pattern) 
			abbr_expansion_reg = re.compile(pattern, re.IGNORECASE)
            
			for match in abbr_expansion_reg.finditer(text):
				full = match.group(1).lower().strip()
				full_beg = match.start()
				full_end = match.start() + len(full)
				if full != "":
					abbr = match.group(2)
					abbr_beg = match.group(0).find(abbr) + full_beg
					abbr_end = abbr_beg + len(abbr)
					abbr_list.add((full, abbr, full_beg, full_end, abbr_beg, abbr_end))
					abbr_set.add((full, abbr))

                    
		for abbr_num_match in abbr_num_reg.finditer(text):
			abbr_num = abbr_num_match.group(1)
			symbols = re.findall("\w", abbr_num)
			num = abbr_num_match.group(2)
            
			pattern = "\\b"
			for i in range(0, len(symbols)):
				pattern = pattern + symbols[i] + "[a-z-]*[\s-]+(?:[a-z]{1,3}[\s-]+)?"
            
			pattern = "(" + pattern + "(?:" + num + ")" + "?" + '\s*' + '(?:[a-z]{1,7}[\s-]+)?' + ")" + "\(\s*" + "(" + abbr_num + num + ")" + "\s*\)"
			#print(abbr_num, symbols, num, pattern) 
			abbr_expansion_reg = re.compile(pattern, re.IGNORECASE)   
            
			for match in abbr_expansion_reg.finditer(text):
				full = match.group(1).lower().strip()
				full_beg = match.start()
				full_end = match.start() + len(full)
				if full != "":
					abbr = match.group(2)
					abbr_beg = match.group(0).find(abbr) + full_beg
					abbr_end = abbr_beg + len(abbr)
					abbr_list.add((full, abbr, full_beg, full_end, abbr_beg, abbr_end))
					abbr_set.add((full, abbr))
        
		self.abbreviations = abbr_list

		abbr_dict = {}
		for item in abbr_set:
			full = item[0]
			abbr = item[1]
			if abbr not in abbr_dict.keys():
				abbr_dict[abbr] = full
			else:
				print("The abbreviation {0} has two full forms: {1} and {2}".format(abbr, abbr_dict[abbr], full))

		self.abbr_dict = abbr_dict

		return abbr_list


	def find_abstract(self):
		text = self.text
		# old version
		# abstr_reg = re.compile("\\b((?:a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\\b|s\s*u\s*m\s*m\s*a\s*r\s*y|s\s*y\s*n\s*o\s*p\s*s\s*i\s*s)\s*(\s*(?:Background|Objective|Question|Discussion|Importance|Relevance|Setting|Interventions?|Outcomes?|Assessments|Measures?|Design|Participants|Subjects|Method(?:s|ology)?|Results|Findings|Conclusions?|Registration|Limitations|Funding).{1,2000}?\n+){3,10}\n*)\s*(?:Background|Introduction|Key[ -]?words|Method(?:s|ology)?)", re.DOTALL | re.IGNORECASE)	

		abstr_reg = re.compile("(\s*\\b(?:a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\\b|s\s*u\s*m\s*m\s*a\s*r\s*y|s\s*y\s*n\s*o\s*p\s*s\s*i\s*s)\s*(\s*(?:Background|Introduction|Objective|Aim|Question|Discussion|Importance|Relevance|Setting|Interventions?|Outcomes?|Assessments|Measures?|Design|Participants|Subjects|Materials|Method(?:s|ology)?|Results|Findings|Conclusions?|Registration|Limitations|Funding).{1,2000}?\n+){3,10}\n*)\s*(?:Background|Introduction|Key[ -]?words|©.{0,20}\d{4}|Copyright.{0,20}\d{4}|All rights reserved)", re.DOTALL | re.IGNORECASE)	
		abstr_match = abstr_reg.search(text)
		abstr = ''
		title = ''
		bt = text
		type = 0
		if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
			abstr = abstr_match.group(1)
			abstr_beg = abstr_match.start()
			abstr_end = abstr_beg + len(abstr)
			if DEBUG: print(1)

		else:
			abstr_reg = re.compile("\\b(\s*(?:a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\\b|s\s*u\s*m\s*m\s*a\s*r\s*y|s\s*y\s*n\s*o\s*p\s*s\s*i\s*s).{300,4000}?)\n(?:Background|Introduction|Key[ -]?words|Method(?:s|ology)?|©.{0,20}\d{4}|Copyright.{0,20}\d{4}|All rights reserved|\(\s*(?:Arch|Ann|Journ|J\\b)[a-z\s\.-]+?/?\d{4}[\d;:\s-]{5,}\))", re.DOTALL | re.IGNORECASE)
			abstr_match = abstr_reg.search(text)
			if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
				abstr = abstr_match.group(1)
				abstr_beg = abstr_match.start()
				abstr_end = abstr_beg + len(abstr)
				if DEBUG: print(2)

			else:
				abstr_reg = re.compile("\\b(a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\\b\n{0,2}(?:(?:[^\n]{0,4000}[^\.]\n){1,10}[^\n]{1,500}\.\s*?\n|[^\n]{300,4000}))", re.DOTALL | re.IGNORECASE)
				abstr_match = abstr_reg.search(text)
				if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
					abstr = abstr_match.group(1)
					abstr_beg = abstr_match.start()
					abstr_end = abstr_beg + len(abstr)
					if DEBUG: print(3)

				else:
					abstr_reg = re.compile("(Background|Objective|Aim|Purpose|Design|Method(?:s|ology)?).{100,4000}?\n(?:Background|Introduction|Key[ -]?words|Method(?:s|ology)?|©.{0,20}\d{4}|Copyright.{0,20}\d{4}|All rights reserved|\(?\s*(?:Arch|Ann|Journ|J\\b)[a-z\s\.-]+?/?\d{4}[\d;:\s-]{5,}\)?)", re.DOTALL | re.IGNORECASE)
					#abstr_reg = re.compile("\n([^\r\n]{0,20}(?:Background|Objective|Aim|Purpose|Question|Discussion|Importance|Relevance|Setting|Interventions?|Outcomes?|Assessments|Measures?|Design|Participants|Method(?:s|ology)?|Results|Findings|Conclusions?|Registration|Limitations|Funding)[^\r\n]{0,20}[\s:]+[^\r\n]{1,1500}[\n\.]+){3,10}", re.DOTALL | re.IGNORECASE)
					abstr_match = abstr_reg.search(text)
					if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
						abstr = abstr_match.group(0)
						abstr_beg = abstr_match.start()
						abstr_end = abstr_beg + len(abstr)
						if DEBUG: print(4)

					else:
						abstr_reg = re.compile("\\A(.{500,4000}?)\s*\(\s*(?:Arch|Ann|Journ|J\\b)[a-z\s\.-]+?/?\d{4}[\d;:\s-]{5,}\)", re.DOTALL | re.IGNORECASE)      
						abstr_match = abstr_reg.search(text)
						if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
							abstr = abstr_match.group(0)
							abstr_beg = abstr_match.start()
							abstr_end = abstr_beg + len(abstr)
							if DEBUG: print(5)

						else:
							abstr_reg = re.compile("(Background|Objective|Aim|Purpose|Question|Design|Method(?:s|ology)?)s?\s*?[\r\n:\.]+\s*.{100,3000}(?:Discussion|Importance|Relevance|Result|Conclusion|Registration|Limitation|Funding)s?\s*?[\r\n:\.]+\s*(?:(?:[^\r\n]{0,1500}[^\.][\r\n]+){1,10}[^\r\n]{0,500}\.\s*?[\r\n]+|[^\r\n]{1,1500})", re.DOTALL | re.IGNORECASE)
							#abstr_reg = re.compile("\n([^\r\n]{0,20}(?:Background|Objective|Aim|Purpose|Question|Discussion|Importance|Relevance|Setting|Interventions?|Outcomes?|Assessments|Measures?|Design|Participants|Method(?:s|ology)?|Results|Findings|Conclusions?|Registration|Limitations|Funding)[^\r\n]{0,20}[\s:]+[^\r\n]{1,1500}[\n\.]+){3,10}", re.DOTALL | re.IGNORECASE)
							abstr_match = abstr_reg.search(text)
							if abstr_match and float(abstr_match.start()) / len(text) <= 0.2:
								abstr = abstr_match.group(0)
								abstr_beg = abstr_match.start()
								abstr_end = abstr_beg + len(abstr)
								if DEBUG: print(6)

							else:
								abstr_reg = re.compile("\\A(.{500,4000}?)\n\s*(?:©.{0,20}\d{4}|Copyright.{0,20}\d{4}|All rights reserved)", re.DOTALL | re.IGNORECASE)
								abstr_match = abstr_reg.search(text)
								if abstr_match:
									abstr = abstr_match.group(1)
									abstr_beg = abstr_match.start()
									abstr_end = abstr_beg + len(abstr)
									if DEBUG: print(7)

								else:
									abstr_reg = re.compile("\n((?:s\s*u\s*m\s*m\s*a\s*r\s*y|s\s*y\s*n\s*o\s*p\s*s\s*i\s*s)\n{0,2}(?:(?:[^\n]{0,4000}[^\.]\n){1,10}[^\n]{0,500}\.\s*?\n|[^\n]{300,4000}))", re.DOTALL | re.IGNORECASE)
									abstr_match = abstr_reg.search(text)
									if abstr_match and float(abstr_match.start()) / len(text) <= 0.1:
										abstr = abstr_match.group(1)
										abstr_beg = abstr_match.start()
										abstr_end = abstr_beg + len(abstr)
										if DEBUG: print(8)

		if abstr != '':
			title = text[:abstr_beg]

			bt = text.replace(title, '', 1)
			bt = bt.replace(abstr, '', 1)

			self.title = (title, 0, len(title))
			self.abstract = (abstr, abstr_beg, abstr_end)
			self.body = (bt, abstr_end + 1, abstr_end + 1 + len(bt)) 

			"""concl_reg = re.compile("([iI]n conclusion|C[oO][nN][cC][lL][uU][sS][iI][oO][nN]|I[nN][tT][eE][rR][pP][rR][eE][tT][aA][tT][iI][oO][nN]).*", re.DOTALL)
			res_reg = re.compile("(R[eE][sS][uU][lL][tT]|F[iI][nN][dD][iI][nN][gG][sS]).*", re.DOTALL)
			concl_match = concl_reg.search(abstr)
			if concl_match:
				concl = concl_match.group(0)
				concl_beg = concl_match.start()
				concl_end = concl_match.end()
				res_match = res_reg.search(abstr[:concl_beg])
				if res_match:
					res = res_match.group(0)
					res_beg = res_match.start()
					res_end = res_match.end()
					abstract = (abstr[:res_beg], res, concl)
				else:
					abstract = (abstr[:concl_beg], '', concl)

			else:
				res_match = res_reg.search(abstr)
				if res_match:
					res = res_match.group(0)
					res_beg = res_match.start()
					res_end = res_match.end()
					abstract = (abstr[:res_beg], res, '')
				else:
					abstract = (abstr, '', '')"""

			bert_input = []
			if self.sentences == []:
				self.sent_split()
			for sent_id, sent in enumerate(self.sentences):
				sent_text = sent[0]
				sent_beg = sent[1]
				sent_end = sent[2]

				if sent_beg <= abstr_beg and sent_end > abstr_beg:
					bert_input.append((sent_text, sent_id))
				elif sent_beg >= abstr_beg and sent_end <= abstr_end:
					bert_input.append((sent_text, sent_id))
				elif sent_beg >= abstr_beg and sent_beg <= abstr_end:
					bert_input.append((sent_text, sent_id))

			if len(bert_input) == 0: print('ERROR empty input for BERT')

			results, labels = run_classifier.main(bert_input, 'sent')

			os.remove("tmp/predict.tf_record")

			res_sents = []
			concl_sents = []
			for (i, probabilities) in enumerate(results):
				# Get the indices of maximum element in numpy array
				class_res = labels[np.where(probabilities == np.amax(probabilities))[0][0]]
				print(bert_input[i], class_res)
				if class_res == 'RESULTS':
					res_sents.append(bert_input[i][1])
				elif class_res == 'CONCLUSIONS':
					concl_sents.append(bert_input[i][1])

			if len(res_sents) != 0:
				print(res_sents)
				res_beg = self.sentences[min(res_sents)][1]
				res_end = self.sentences[max(res_sents)][2]
				res_text = self.text[res_beg:res_end + 1]
				self.results = (res_text, res_beg, res_end)

			if len(concl_sents) != 0:
				print(concl_sents)
				concl_beg = self.sentences[min(concl_sents)][1]
				concl_end = self.sentences[max(concl_sents)][2]
				concl_text = self.text[concl_beg:concl_end + 1]
				self.conclusions = (concl_text, concl_beg, concl_end)

			if res_text != '' and concl_text != '':
				abstract = (abstr[:min(res_beg, concl_beg)], res_text, concl_text)
			elif res_text != '':
				abstract = (abstr[:res_beg], res_text, '')
			elif concl_text != '':
				abstract = (abstr[:concl_beg], '', concl_text)
			else:
				abstract = (abstr, '', '')

		else:
			abstract = ('', '', '')

			self.title = ''
			self.abstract = ''
			self.body = (self.text, 0, len(text)) 

		return (title, abstract, bt)



	def find_abstr_sections(self):
		abstr = self.text
		
		self.abstract = (abstr, 0, len(abstr))
                
		"""concl_reg = re.compile("([iI]n conclusion|Conclusion|Interpretation).*", re.DOTALL | re.IGNORECASE)
		res_reg = re.compile("(Result|Findings).*", re.DOTALL | re.IGNORECASE)
		concl_match = concl_reg.search(abstr)
		if concl_match:
			concl = concl_match.group(0)
			concl_beg = concl_match.start()
			concl_end = concl_match.end()
			res_match = res_reg.search(abstr[:concl_beg])
			if res_match:
				res = res_match.group(0)
				res_beg = res_match.start()
				res_end = res_match.end()
				abstract = (abstr[:res_beg], res, concl)
			else:
				abstract = (abstr[:concl_beg], '', concl)
				
		else:
			res_match = res_reg.search(abstr)
			if res_match:
				res = res_match.group(0)
				res_beg = res_match.start()
				res_end = res_match.end()
				abstract = (abstr[:res_beg], res, '')
			else:
				abstract = (abstr, '', '')

		if abstract[1] != '':
			self.results = (abstract[1], abstr.find(abstract[1]), abstr.find(abstract[1]) + len(abstract[1]))
		if abstract[2] != '':
			self.conclusions = (abstract[2], abstr.find(abstract[2]), abstr.find(abstract[2]) + len(abstract[2]))"""

		abstr_sentences = []
		bert_input = []
		if self.sentences == []:
			self.sent_split()
		for sent_id, sent in enumerate(self.sentences):
			bert_input.append((sent_text, sent_id))

		if len(bert_input) == 0: print('ERROR empty input for BERT')

		results, labels = run_classifier.main(bert_input, 'sent')

		os.remove("tmp/predict.tf_record")

		res_sents = []
		concl_sents = []
		for (i, probabilities) in enumerate(results):
			# Get the indices of maximum element in numpy array
			class_res = labels[np.where(probabilities == np.amax(probabilities))[0][0]]
			if class_res == 'RESULTS':
				res_sents.append(bert_input[i][1])
			elif class_res == 'CONCLUSIONS':
				concl_sents.append(bert_input[i][1])

		if len(res_sents) != 0:
			res_beg = self.sentences[min(res_sents)][1]
			res_end = self.sentences[max(res_sents)][2]
			res_text = self.text[res_beg:res_end + 1]
			self.results = (res_text, res_beg, res_end)

		if len(concl_sents) != 0:
			concl_beg = self.sentences[min(concl_sents)][1]
			concl_end = self.sentences[max(concl_sents)][2]
			concl_text = self.text[concl_beg:concl_end + 1]
			self.conclusions = (concl_text, concl_beg, concl_end)

		if res_text != '' and concl_text != '':
			abstract = (abstr[:min(res_beg, concl_beg)], res_text, concl_text)
		elif res_text != '':
			abstract = (abstr[:res_beg], res_text, '')
		elif concl_text != '':
			abstract = (abstr[:concl_beg], '', concl_text)
		else:
			abstract = (abstr, '', '')

		return abstract



	def preannot_po_biobert(self, parser = 'bert'):
		text = self.text
		pattern_po = re.compile('\\b(primary|main|first|principal|final|key|secondary)\s+(\w+\s+){0,3}(outcome|end[ -]*point|measure|variable|assessment|parameter|criteri)', re.IGNORECASE)

		if self.sentences == []:
			self.sent_split()

		outcomes = []
		sent_list = []
		ind = 0

		with open('tmp/out/test.tsv', 'w') as input_file:
			for sent_id, sent in enumerate(self.sentences): #tqdm(self.sentences):
				sent_text = sent[0] #.strip()
				sent_text = sent_text.replace('end point', 'end-point')
				sent_beg = sent[1]
				sent_end = sent[2]
				if pattern_po.search(sent_text):
					sent_list.append(sent_id)
					if (sent_id, parser) not in self.sentences_tagged.keys():
						sent_toks = self.bert_tokenize_sent(do_lower=FLAGS.po_do_lower_case, sentence = sent_text)
						self.sentences_tagged[(sent_id, parser)] = sent_toks
								
					for token in self.sentences_tagged[(sent_id, parser)]:
						tok = token[0]
						tok = tok.strip()
						if tok != '':
							input_file.write(tok + ' O\n')
						else:
							input_file.write(tok.__repr__() + ' O\n')
						ind += 1
					input_file.write('\n')

		input_file.close()

		run_ner.main('po')
		ner_detokenize.detokenize('tmp/out/test.tsv', 'tmp/token_test.txt', 'tmp/label_test.txt', 'tmp/po_res.txt')

		res_file = codecs.open('tmp/po_res.txt', 'r', encoding = 'utf-8')
		all_sent_res = res_file.read()
		res_file.close()

		entity = "Out"
		typ = 'Type="Prim" Status="Declared"'		

		outcomes = []
		res_by_sent = all_sent_res.split('\n\n')
		for sent_id, res in zip(sent_list, res_by_sent):
			out_beg = None
			out_end = None
			res_tok = res.split('\n')
			#print(res_tok)
			for i, res_line in enumerate(res_tok):
				tok = res_line[:res_line.find(' ')]
				tag = res_line[res_line.find(' ') + 1:].strip()
				print(i, tok, tag)
				if tag == 'O':
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
						out_beg = None
						out_end = None
				elif tag == 'B':
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
					out_beg = i
					out_end = i
				elif tag == 'I':
					if out_beg != None and out_end != None:
						out_end = i
					else:
						out_beg = i
						out_end = i

				if i == len(res_tok):
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
						out_beg = None
						out_end = None				

		for f in os.listdir('tmp'):
			f_path = os.path.join('tmp', f)
			if os.path.isfile(f_path):
				os.remove(f_path)
			else:
				for f1 in os.listdir(f_path):
					os.remove(os.path.join(f_path, f1))


		for out in outcomes:
			if self.outcomes_declared == None:
				self.outcomes_declared = [out]
			else:
				self.outcomes_declared.append(out)


		return outcomes

	def preannot_rep_scibert(self, parser = 'bert'):
		text = self.text
		pattern_signif = re.compile('(signific|p[- ]?value|\\bp\\b)', re.IGNORECASE)

		if self.sentences == []:
			self.sent_split()

		results = set()
		
		outcomes = []
		if self.abstract == None:
			self.find_abstract()

		if self.abstract != '':
			abstr_beg = self.abstract[1]
			abstr_end = self.abstract[2]
		
		sent_list = []
		ind = 0

		with open('tmp/out/test.tsv', 'w') as input_file:
			for sent_id, sent in enumerate(self.sentences): #tqdm(self.sentences):
				sent_text = sent[0] #.strip()
				sent_text = sent_text.replace('end point', 'end-point')
				sent_beg = sent[1]
				sent_end = sent[2]
				if (pattern_signif.search(sent_text) or (self.abstract != '' and sent_beg >= abstr_beg and sent_end <= abstr_end)) and not sent_text.count('\n') > 5:
					sent_list.append(sent_id)
					if (sent_id, parser) not in self.sentences_tagged.keys():
						sent_toks = self.bert_tokenize_sent(do_lower=FLAGS.rep_do_lower_case, sentence = sent_text)
						self.sentences_tagged[(sent_id, parser)] = sent_toks
								
					for token in self.sentences_tagged[(sent_id, parser)]:
						tok = token[0]
						tok = tok.strip()
						if tok != '':
							input_file.write(tok + ' O\n')
						else:
							input_file.write(tok.__repr__() + ' O\n')
						ind += 1
					input_file.write('\n')

		input_file.close()

		run_ner.main('rep')
		ner_detokenize.detokenize('tmp/out/test.tsv', 'tmp/token_test.txt', 'tmp/label_test.txt', 'tmp/rep_res.txt')

		res_file = codecs.open('tmp/rep_res.txt', 'r', encoding = 'utf-8')
		all_sent_res = res_file.read()
		res_file.close()

		entity = "Out"
		typ = 'Type="None" Status="Reported"'		

		outcomes = []
		res_by_sent = all_sent_res.split('\n\n')
		for sent_id, res in zip(sent_list, res_by_sent):
			out_beg = None
			out_end = None
			res_tok = res.split('\n')
			#print(res_tok)
			for i, res_line in enumerate(res_tok):
				tok = res_line[:res_line.find(' ')]
				tag = res_line[res_line.find(' ') + 1:].strip()
				print(i, tok, tag)
				if tag == 'O':
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
						out_beg = None
						out_end = None
				elif tag == 'B':
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
					out_beg = i
					out_end = i
				elif tag == 'I':
					if out_beg != None and out_end != None:
						out_end = i
					else:
						out_beg = i
						out_end = i

				if i == len(res_tok):
					if out_beg != None and out_end != None:
						outcomes.append((entity, out_beg, out_end, sent_id, typ, 0, None))
						out_beg = None
						out_end = None				

		for f in os.listdir('tmp'):
			f_path = os.path.join('tmp', f)
			if os.path.isfile(f_path):
				os.remove(f_path)
			else:
				for f1 in os.listdir(f_path):
					os.remove(os.path.join(f_path, f1))

		for out in outcomes:
			if self.outcomes_reported == None:
				self.outcomes_reported = [out]
			else:
				self.outcomes_reported.append(out)
		return outcomes


	def preannot_stat(self, parser = 'spacy'):

		#print("Searching for statistical measures")

		p_reg = re.compile("\\bp([ -]*value)?[<>=≤≥: ]+\d*[\.,]\d+\\b", re.IGNORECASE)

		#self.unescape_xml()
		text = self.text
		pattern = re.compile('(\\bp\\b|CI|confidence|interval|p[ -]?val|significan)', re.IGNORECASE)

		if self.sentences == []:
			self.sent_split()

		results = set()
		sent_id = 0
		for sent in self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				tags = self.sentences_tagged[(sent_id, parser)]

				for p_match in p_reg.finditer(sent_text):
					p_beg = p_match.start()
					p_end = p_match.end()
					for tok in tags:
						tok_start = tok[3]
						tok_end = tok[4]
						if tok_start <= p_beg and p_beg <= tok_end:
							p_beg_tok = tags.index(tok)
						if tok_end == p_end:
							p_end_tok = tags.index(tok)
					results.add(('StatMeas', p_beg_tok, p_end_tok, sent_id, 'Type="Pval"', 0))


				tokens = []
				text_tagged = []
				num = 0
				for item in tags:
					text_tagged.append((item[0], item[1], item[2], num))
					tokens.append(item[0])
					num = num + 1

				#Find Components + positions
				# P-value
				pval = []

				# Confidence interval
				ci = []

				for item in text_tagged:
					num = text_tagged.index(item)

					if check_token(num, text_tagged, lemma_list = ['significan'], reg = True):
						results.add(('StatMeas', num, num, sent_id, 'Type="Pval"', 0))
						
						i = num
						while check_left(i, text_tagged, pos_list = ['RB', 'RBR', 'RBS', 'JJ', 'JJR', 'JJS', 'DT'], lemma_not_list = ['no', 'not', 'non', 'none'], mode_pos = 'AND') or check_left(i, text_tagged, lemma_list = ['of', 'to']) or check_left(i, text_tagged, pos_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHG', 'VHN', 'VHP', 'VHZ', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ'], lemma_not_list = ['fail'], mode_pos = 'AND') or  check_left(i, text_tagged, lemma_list = ['-']):
							i -= 1
							
						if check_left(i, text_tagged, lemma_list = ['no', 'not', 'non', 'none', 'lack', 'fail', 'failure', 'without']):
							results.add(('StatMeas', i - 1, num, sent_id, 'Type="Pval"', 0))

					elif check_token(num, text_tagged, lemma_list = [u'p', "p's", u'pvalue', u'p-value']):
						pval.append((num, num))

						if check_right(num, text_tagged, lemma_list = [u'value', u'level']):
							pval.append((num, num + 1))
		
						elif check_right(num, text_tagged, lemma_list = [u'-']):
							if check_right(num + 1, text_tagged, lemma_list = [u'value', u'level']):
								pval.append((num, num + 2))

					elif check_token(num, text_tagged, lemma_list = [u'CI', u'ci']):
						ci.append((num, num))

					elif check_token(num, text_tagged, lemma_list = [u'confidence']):
						if check_right(num, text_tagged, lemma_list = [u'interval']):
							ci.append((num, num + 1))
		

				#print("First level components collected")

				# STATISTICAL MEASURES

				# P-value
				for item in pval:
					beg = item[0]
					end = item[1]

					i = end
					while check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'DT', 'PDT', 'NN', 'NNS', 'NN+POS', 'NNS+POS', 'NP+POS', 'VVG', 'VVN', 'IN'], lemma_not_list = [u'of', u'be', u'>', u'<', u'=', u'≤', u'≥'], ):
						i = i + 1

					while check_right(i, text_tagged, lemma_list = [u'of', u'be', u'>', u'<', u'=', u'≤', u'≥', u':', 'adj'], pos_list = ['_SP']):
						i = i + 1

						if check_right(i, text_tagged, pos_list = ['CD'], lemma_list = ['ns']) or check_right(i, text_tagged, lemma_list = ['\.?\d+[\.,]?\d*'], reg = True):
							i = i + 1
							results.add(('StatMeas', beg, i, sent_id, 'Type="Pval"', 0))

							while check_right(i, text_tagged, lemma_list = ['and', ',']):
								i = i + 1
								if check_right(i, text_tagged, pos_list = ['CD'], lemma_list = ['ns']):
									i = i + 1
									results.add(('StatMeas', i, i, sent_id, 'Type="Pval"', 0))				
		

				# Confidence intervals
				for item in ci:
					beg = item[0]
					end = item[1]
					#print(tokens[beg:end + 1])

					if check_left(beg, text_tagged, lemma_list = [u'%']):
						if check_left(beg - 1, text_tagged, pos_list = ['CD']):
							i = end
							if check_right(end, text_tagged, lemma_list = [u',', u':']):
								i = end + 1	
							if check_right(i, text_tagged, pos_list = ['CD']):
								end_ci = i + 1
								if check_right(end_ci, text_tagged, pos_list = ['NN', 'NNS', 'NP', 'NPS']):
									end_ci = end_ci + 1
								if check_right(end_ci, text_tagged, lemma_list = [u'to', u'-', u'–', u',']):
									if check_right(end_ci + 1, text_tagged, pos_list = ['CD']):
										end_ci = end_ci + 2

								results.add(('StatMeas', beg - 2, end_ci, sent_id, 'Type="CI"', 0))

			#print("Sentence {0} out of {1} processed".format(sent_id, len(self.sentences)))
			sent_id += 1

		self.stats = results
		return results

	        # end preannotation of statistical measures (Pval, CI)


	def preannot_noninf(self, parser = 'spacy'):

		print("Searching for indicators of non-inferiprity/equivalence design")

		#self.unescape_xml()
		text = self.text
		pattern = re.compile('(infer|equivalen|equal|comparab|similar)', re.IGNORECASE)

		if self.sentences == []:
			self.sent_split()


		results = set()
		sent_id = 0
		for sent in self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				tags = self.sentences_tagged[(sent_id, parser)]


				tokens = []
				text_tagged = []
				num = 0
				for item in tags:
					text_tagged.append((item[0], item[1], item[2], num))
					tokens.append(item[0])
					num = num + 1

				#Find Components + positions
				for item in text_tagged:
					num = text_tagged.index(item)


					# Non-inferiority design + similarity
					noninf = 0
					if check_token(num, text_tagged, token_list = [u'(?:non|not)-?inferior'], reg = True):
						beg = num
						noninf = 1

					elif check_token(num, text_tagged, token_list = [u'inferior'], reg = True):
						if check_left(num, text_tagged, token_list = [u'-']):
							if check_left(num - 1, text_tagged, token_list = [u'non', u'not']):
								beg = num - 2
								noninf = 1
						elif check_left(num, text_tagged, token_list = [u'non', u'not']):
							beg = num - 1
							noninf = 1
	
					if noninf == 1:
						i = num
						while check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'NN', 'NNS', 'NP', 'NPS', 'NN+POS', 'NNS+POS', 'NP+POS', 'NPS+POS', 'VVG', 'VVN'], lemma_not_list = ['study', 'trial', 'analysis', 'test', 'margin', 'criterion', 'criterium', 'methodology', 'limit', 'hypothesis', 'design', 'comparison']):
							i = i + 1
						if check_right(i, text_tagged, lemma_list = [u'study', u'trial', u'analysis', u'test', u'margin', u'criterion', u'criterium', u'methodology', u'limit', u'hypothesis', u'design', u'comparison']):				
							results.add(('StudySubType', beg, i + 1, sent_id, 'SubType="Noninf"', 0))
						#else:
							#results.add(('Sim', beg, num, sent_id, 'SubType="Noninf"', 0))

					if check_token(num, text_tagged, lemma_list = [u'objective', u'aim', u'purpose', u'design', u'assess', u'hypothesis']):
						i = num
						while i < len(text_tagged) and not check_right(i, text_tagged, pos_list = ['SENT'], lemma_list = [u'as', u'that', u'of', u'to', u':']):
							i = i + 1
						if check_right(i, text_tagged, lemma_list = [u'as', u'that', u'of', u'to', u':']):
							i = i + 1
							k = i + 1
							while i < len(text_tagged) and not check_right(i, text_tagged, pos_list = ['SENT']) and not check_right(i, text_tagged, token_list = [u'(((?:non|not)-?)?inferior|equivalence)'], reg = True):
								i = i + 1
							if check_right(i, text_tagged, token_list = [u'(((?:non|not)-?)?inferior|equivalence)'], reg = True):
								results.add(('StudySubType', num, i + 1, sent_id, 'SubType="Noninf"', 0))

							while k < len(text_tagged) and not check_right(k, text_tagged, pos_list = ['SENT']) and not check_right(k, text_tagged, token_list = [u'(equal|equivalen|comparab|similar)'], reg = True) and not check_right(k, text_tagged, lemma_list = [u'efficacy', u'effect', u'effectiveness', u'tolerability', u'potency', u'activity', u'incidence', u'safety', u'tolerability', u'response', u'outcome', u'impact', u'effective', u'efficacious']):
								k = k + 1
							if check_right(k, text_tagged, token_list = [u'(equal|equivalen|comparab|similar)'], reg = True):
								if check_right(k + 1, text_tagged, lemma_list = [u'efficacy', u'effect', u'effectiveness', u'tolerability', u'potency', u'activity', u'incidence', u'safety', u'tolerability', u'response', u'outcome', u'impact', u'effective', u'efficacious']):
									results.add(('StudySubType', num, k + 2, sent_id, 'SubType="Noninf"', 0))

							elif check_right(k, text_tagged, lemma_list = [u'efficacy', u'effect', u'effectiveness', u'tolerability', u'potency', u'activity', u'incidence', u'safety', u'tolerability', u'response', u'outcome', u'impact', u'effective', u'efficacious']):
								if check_right(k + 1, text_tagged, token_list = [u'(equal|equivalen|comparab|similar)'], reg = True):
									results.add(('StudySubType', num, k + 2, sent_id, 'SubType="Noninf"', 0))


			#print("Sentence {0} out of {1} processed".format(sent_id, len(self.sentences)))
			sent_id += 1

		return results

	        # end preannotation for non-inferiority design


	def find_eval_synt(self, parser = 'spacy'):
		#self.unescape_xml()
		text = self.text
		pattern = re.compile('(efficac|effect|tolerab|tolerated|poten|activ|safe|good|equal|equivalen|comparabl|simil)', re.IGNORECASE)

		out_adj_list = ['efficacious', 'effective', 'tolerable', 'well-tolerated', 'tolerated', 'potent', 'active', 'safe', 'good', 'high']
		out_noun_list = [u'efficacy', u'effect', u'effectiveness', u'tolerability', u'potency', u'activity', u'incidence', u'safety', u'tolerability', u'response', u'improvement', u'outcome', u'reduction', u'increase', u'decrease', u'change', u'symptom', u'impact', u'elevation', u'effective', u'efficacious', u'result', u'benefit', u'satisfaction', u'burden', u'gain', u'end', u'end-point', u'event']
		out_verb_list = [u'increase', u'decline', u'decrease', u'improve', u'ameliorate', u'elevate', u'reduce', u'enhance', u'lower', u'gain', u'drop', u'raise', 'lose',  'worsen', 'attenuate', 'fall', 'change', 'impact', 'influence']
		group_list = [u'placebo', u'group', u'control', u'dose', u'patient', u'controls', u'arm', u'treatment', u'intervention']
		verb_list = [u'have', u'show', u'see', u'observe', u'find', u'indicate', u'demonstrate', u'exhibit', u'produce', u'achieve', u'result', u'seem', u'appear', u'prove', u'improve', u'perform', u'occur', u'increase', u'decrease', u'benefit', u'yield', u'induce', u'display', u'reach', u'incur', u'report', u'respond', u'act', 'be', 'provide']
		sim_adj_list = ['equal', 'equivalent', 'comparable', 'similar', 'same', 'identical', 'non-inferior', 'noninferior']
		sim_noun_list = ['equality', 'equivalence', 'comparability', 'similarity', 'similitude', 'non-inferiority', 'noninferiority']
		sim_adv_list = ['equally', 'equivalently', 'comparably', 'similarly', 'identically']
		interv = [u'active', u'controller', u'placebo', u'drug', u'medication', u'treatment', u'agent', u'therapy', u'medicine', u'intervention', u'neuroleptic', u'antipsychotic', u'antidepressant', 'care', 'protocol', 'regimen']

		if self.sentences == []:
			self.sent_split()

		results = set()
		sent_id = 0
			
		for sent in self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				doc = self.sentences_depparsed[(sent_id, parser)]		
			
				eval_found = False
				for token_parsed in doc:
					token = token_parsed[0]
					head = token.head
					children = token.children

					if parser == 'spacy':
						head_children = head.children
						head_head = head.head
						head_head_children = head_head.children
						head_head_head = head_head.head
					elif parser == 'stanfordcorenlp' or parser == 'malt' or parser == 'bllipparser':
						head_children = stanford_children(head)
						head_head = stanford_head(head)
						head_head_children = stanford_children(head_head)
						head_head_head = stanford_head(head_head)

					if token.lemma_ in interv:
						if head.lemma_ in verb_list:
							for head_child in head.children:
								if head_child.lemma_ in out_adj_list + out_noun_list:
									eval_ind = token.i
									eval_found = True

						if head.lemma_ in out_verb_list:
							eval_ind = token.i
							eval_found = True


				if eval_found:
					results.add(('Eval', eval_ind, eval_ind, sent_id, '', 0))


			#print("Sentence {0} out of {1} ".format(sent_id, len(self.sentences)))
		return results

	def find_hedge_synt(self, parser = 'spacy'):
		#self.unescape_xml()
		print('Searching for hedging')
		text = self.text
		pattern = re.compile('(may|might|can|could|would|possib|potential|seem|appear|suggest)', re.IGNORECASE)

		modal_verbs_list = ['may', 'might', 'can', 'could', 'would']
		seem_list = ['seem', 'appear', 'suggest']
		adv_list = ['potentially', 'possibly']
		adj_list = ['potential', 'possible']


		if self.sentences == []:
			self.sent_split()

		results = set()
		sent_id = 0
			
		for sent in self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				doc = self.sentences_depparsed[(sent_id, parser)]		
			
				for token_parsed in doc:
					token = token_parsed[0]
					head = token.head
					children = token.children

					if parser == 'spacy':
						head_children = head.children
						head_head = head.head
						head_head_children = head_head.children
						head_head_head = head_head.head
					elif parser == 'stanfordcorenlp' or parser == 'malt' or parser == 'bllipparser':
						head_children = stanford_children(head)
						head_head = stanford_head(head)
						head_head_children = stanford_children(head_head)
						head_head_head = stanford_head(head_head)

					if token.text.lower() in modal_verbs_list:
						if head.tag_.find('V') == 0:
							results.add(('Hedge', min(token.i, head.i), max(token.i, head.i), sent_id, '', 0))

					elif token.lemma_ in seem_list:
						for child in children:
							if child.tag_.find('V') == 0:
								results.add(('Hedge', min(token.i, child.i), max(token.i, child.i), sent_id, '', 0))

					if token.text.lower() in adv_list:
						if head.tag_.find('V') == 0 or head.tag_.find('J') == 0:
							results.add(('Hedge', min(token.i, head.i), max(token.i, head.i), sent_id, '', 0))

					elif token.lemma_ in adj_list:
						if head.tag_.find('N') == 0:
							results.add(('Hedge', min(token.i, head.i), max(token.i, head.i), sent_id, '', 0))

			sent_id += 1

			#print("Sentence {0} out of {1} ".format(sent_id, len(self.sentences)))
		return results


	def find_sim_synt(self, parser = 'spacy'):
		#self.unescape_xml()
		print('Searching for similarity statements')
		text = self.text
		pattern = re.compile('(efficac|effect|tolerab|tolerated|poten|activ|safe|good|equal|equivalen|comparabl|simil|same)', re.IGNORECASE)

		out_adj_list = ['efficacious', 'effective', 'tolerable', 'well-tolerated', 'tolerated', 'potent', 'active', 'safe', 'good', 'high']
		out_noun_list = [u'efficacy', u'effect', u'effectiveness', u'tolerability', u'potency', u'activity', u'incidence', u'safety', u'tolerability', u'response', u'improvement', u'outcome', u'reduction', u'increase', u'decrease', u'change', u'symptom', u'impact', u'elevation', u'effective', u'efficacious', u'result', u'benefit', u'satisfaction', u'burden', u'gain', u'end', u'end-point', u'event']
		out_verb_list = [u'increase', u'decline', u'decrease', u'improve', u'ameliorate', u'elevate', u'reduce', u'enhance', u'lower', u'gain', u'drop', u'raise', 'lose',  'worsen', 'attenuate', 'fall', 'change', 'impact', 'influence']
		group_list = [u'placebo', u'group', u'control', u'dose', u'patient', u'controls', u'arm', u'treatment', u'intervention']
		verb_list = [u'have', u'show', u'see', u'observe', u'find', u'indicate', u'demonstrate', u'exhibit', u'produce', u'achieve', u'result', u'seem', u'appear', u'prove', u'improve', u'perform', u'occur', u'increase', u'decrease', u'benefit', u'yield', u'induce', u'display', u'reach', u'incur', u'report', u'respond', u'act', 'be', 'provide']
		sim_adj_list = ['equal', 'equivalent', 'comparable', 'similar', 'same', 'identical', 'non-inferior', 'noninferior']
		sim_noun_list = ['equality', 'equivalence', 'comparability', 'similarity', 'similitude', 'non-inferiority', 'noninferiority']
		sim_adv_list = ['equally', 'equivalently', 'comparably', 'similarly', 'identically']
		interv = [u'active', u'controller', u'placebo', u'drug', u'medication', u'treatment', u'agent', u'therapy', u'medicine', u'intervention', u'neuroleptic', u'antipsychotic', u'antidepressant', 'care', 'protocol', 'regimen']

		if self.sentences == []:
			self.sent_split()

		if self.abstract == None:
			self.find_abstract()

		if self.results != None and self.conclusions != None:
			beg_search = self.results[1]
			end_search = self.conclusions[2]
		elif self.results != None and self.conclusions == None:
			beg_search = self.results[1]
			end_search = self.results[2]
		elif self.results == None and self.conclusions != None:
			beg_search = self.conclusions[1]
			end_search = self.conclusions[2]
		elif self.results == None and self.conclusions == None:
			beg_search = self.abstract[1]
			end_search = self.abstract[2]

		# find sentence numbers for abstract
		abstr_sent = []
		sent_id = 0
		for sent in self.sentences:
			sent_beg = sent[1]
			sent_end = sent[2]
			if sent_beg <= beg_search and sent_end > beg_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_end <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_beg <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			sent_id += 1

		results = set()
			
		for sent in abstr_sent: # self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			sent_id = sent[3] #self.sentences.index(sent)
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				doc = self.sentences_depparsed[(sent_id, parser)]		
			
				sim_found = False
				demographics_found = False	
				# FIND OUTCOMES
				for token_parsed in doc:
					token = token_parsed[0]
					head = token.head
					children = token.children

					if parser == 'spacy':
						head_children = head.children
						head_head = head.head
						head_head_children = head_head.children
						head_head_head = head_head.head
					elif parser == 'stanfordcorenlp' or parser == 'malt' or parser == 'bllipparser':
						head_children = stanford_children(head)
						head_head = stanford_head(head)
						head_head_children = stanford_children(head_head)
						head_head_head = stanford_head(head_head)

					# Similarity: as X as
					if token.lemma_ in out_adj_list:
						for child in token.children:
							if child.lemma_ == 'as':
								sim_ind = token.i
								sim_found = True

					elif token.lemma_ in sim_noun_list:
						if head.lemma_ in verb_list:
							sim_ind = token.i
							sim_found = True

					elif token.lemma_ in sim_adj_list:
						if head.tag_.find('N') == 0:
							if head.head.lemma_ in verb_list:
								sim_ind = token.i
								sim_found = True

						if head.lemma_ in verb_list:
							sim_ind = token.i
							sim_found = True

						for child in children:
							if child.lemma_ in [u'across', u'between']:
								sim_ind = token.i
								sim_found = True
							elif child.tag_ in ['IN', 'TO']:
								for child_child in child.children:
									if child_child.lemma_ in out_noun_list + group_list:
										sim_ind = token.i
										sim_found = True	

								if child.lemma_ in [u'to', u'with', u'as']:
									for child_child in child.children:
										if child_child.lemma_ in ['that']:
											sim_ind = token.i
											sim_found = True

								elif child.lemma_ == 'in':
									for child_child in child.children:
										if child_child.lemma_ in ['term', 'terms']:
											for child_child_child in child.child.children:
												if child_child_child.lemma_ == 'of':
													for child_child_child_child in child.child.child.children:
														if child_child_child_child.lemma_ in out_noun_list + group_list:
															sim_ind = token.i
															sim_found = True

					elif token.lemma_ in sim_adv_list:
						if head.lemma_ in verb_list + out_verb_list + out_adj_list:
							sim_ind = token.i
							sim_found = True

					elif token.lemma_ in ['demographic', 'demographics', 'baseline', 'demographically']:
						demographics_found = True

					"""elif token.lemma_ in interv:
						quantif_found = False
						for child in children:
							if child.lemma_ in ['both', 'each', 'all', 'either']:
								quantif_found = True
								break
						if quantif_found:
							if head.lemma_ in verb_list:
								sim_ind = token.i
								sim_found = True"""

				if sim_found and (not demographics_found):
					results.add(('Sim', sim_ind, sim_ind, sent_id, '', 0))

			#print("Sentence {0} out of {1} ".format(sent_id, len(self.sentences)))
		return results
		

	def find_wgc_synt(self, parser = 'spacy'):
		#self.unescape_xml()
		print('Searching for within-group comparisons')
		text = self.text
		pattern = re.compile('(ameliorat|chang|declin|decreas|elevat|enhanc|gain|impact|effect|improv|increas|influence|reduc|within.?group)', re.IGNORECASE)

		adj_list = [u'better', u'faster', u'greater', u'higher', u'lower', u'poorer', u'quicker', u'shorter', u'slower', u'worse', 'fewer', 'less', 'lesser']
		noun_list = ['gain', u'decline', u'decrease', u'elevation', u'enhancement', u'improvement', u'amelioration', u'reduction', u'increase', u'rise', u'drop', 'alteration', 'loss', 'fall'] #, u'change', u'difference', u'impact', u'effect'
		verb_list = [u'increase', u'decline', u'decrease', u'improve', u'ameliorate', u'elevate', u'reduce', u'enhance', u'lower', u'gain', u'drop', u'raise', 'lose',  'worsen', 'attenuate', 'fall']
		change_list = [u'change', u'impact', 'effect', u'influence']
		reach_list = ['reach', 'obtain', 'achieve', 'experience', 'have', 'produce', 'note', 'see', 'develop', 'detect', 'sustain', 'show', 'demonstrate']
		effective_list = ['effective', 'efficacious', 'successful', 'efficacy', 'effectiveness']
		patients = [u'patient', u'individual', u'man', u'woman', u'child', u'adolescent', u'adult', u'subject', u'person', u'schizophrenic', u'male', u'female', u'population', u'cohort', u'participant', u'respondent', u'infant', u'newborn', u'neonate', u'smoker', u'non-smoker', 'group', 'arm', 'control']
		interv = [u'active', u'controller', u'placebo', u'drug', u'medication', u'treatment', u'agent', u'therapy', u'medicine', u'intervention', u'neuroleptic', u'antipsychotic', u'antidepressant', 'care', 'protocol', 'regimen']
		
		if self.sentences == []:
			self.sent_split()

		if self.abstract == None:
			self.find_abstract()

		if self.results != None and self.conclusions != None:
			beg_search = self.results[1]
			end_search = self.conclusions[2]
		elif self.results != None and self.conclusions == None:
			beg_search = self.results[1]
			end_search = self.results[2]
		elif self.results == None and self.conclusions != None:
			beg_search = self.conclusions[1]
			end_search = self.conclusions[2]
		elif self.results == None and self.conclusions == None:
			beg_search = self.abstract[1]
			end_search = self.abstract[2]

		# find sentence numbers for abstract
		abstr_sent = []
		sent_id = 0
		for sent in self.sentences:
			sent_beg = sent[1]
			sent_end = sent[2]
			if sent_beg <= beg_search and sent_end > beg_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_end <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_beg <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			sent_id += 1


		results = set()
			
		for sent in abstr_sent: #self.sentences: #tqdm(self.sentences):
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			sent_id = sent[3] #self.sentences.index(sent)
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged
							
				doc = self.sentences_depparsed[(sent_id, parser)]		
			
				wgc_word_found = False	
				comparison_found = False
				modal_found = False
				assoc_found = False
				assess_found = False
				proportion_found = False
				# FIND OUTCOMES
				for token_parsed in doc:
					token = token_parsed[0]
					head = token.head
					children = token.children

					if parser == 'spacy':
						head_children = head.children
						head_head = head.head
						head_head_children = head_head.children
						head_head_head = head_head.head
					elif parser == 'stanfordcorenlp' or parser == 'malt' or parser == 'bllipparser':
						head_children = stanford_children(head)
						head_head = stanford_head(head)
						head_head_children = stanford_children(head_head)
						head_head_head = stanford_head(head_head)

					# patterns with adjectives
					if token.lemma_ in verb_list:
						if token.tag_ in ['VBD', 'VBZ', 'VBN', 'VBG', 'VB']: #.find('V') == 0:
							neg_found = False
							for child in children:
								if child.lemma_ in ['not', u'may', u'can', u'will', u'could', u'would', 'might']:
									neg_found = True

							if not neg_found:
								wgc_ind = token.i
								wgc_word_found = True
								if head.tag_.find('N') == 0:
									if head.head.lemma_ == 'with':
										wgc_word_found = False


						elif head.head.tag_ == 'IN' and head.head.lemma_ in effective_list:
							wgc_ind = token.i
							wgc_word_found = True

						elif head.tag_ in ['VBD', 'VBZ', 'VBN']: #.find('V') == 0:
							neg_found = False
							for child in head.children:
								if child.lemma_ in ['not', u'may', u'can', u'will', u'could', u'would', 'might']:
									neg_found = True
							if not neg_found:
								wgc_ind = token.i
								wgc_word_found = True


					elif token.lemma_ in noun_list and token.tag_.find('N') == 0:
						neg_found = False
						for child in children:
							if child.lemma_ in ['no', 'non', 'none', 'not']:
								neg_found = True
								break
							elif child.tag_ in ['JJR', 'JJS']:
								comparison_found = True
								break

						if not neg_found:
							if head.tag_ in ['VBD', 'VBZ', 'VBN']: #.find('V') == 0:					
								neg_found = False
								for child in head.children:
									if child.lemma_ in ['no', 'non', 'none', 'not']:
										neg_found = True
										break
								if not neg_found:
									wgc_ind = token.i
									wgc_word_found = True

							elif (head.tag_ in ['IN', 'TO'] and head.head.tag_ in ['VBD', 'VBZ', 'VBN']): #.find('V') == 0):						
								neg_found = False
								for child in head.head.children:
									if child.lemma_ in ['no', 'non', 'none', 'not']:
										neg_found = True
										break
								if not neg_found:
									wgc_ind = token.i
									wgc_word_found = True

					elif token.lemma_ in change_list and token.tag_.find('N') == 0:
						chg_word_found = False
						neg_found = False
						for child in children:
							if child.lemma_ == 'significant':
								chg_word_found = True
							elif child.lemma_ in ['no', 'not', 'any', 'none', 'non']:
								neg_found = True
						if chg_word_found and not neg_found:
							wgc_ind = token.i
							wgc_word_found = True	

					elif token.text.lower() in [u'compare', u'compared', u'comparison', u'comparing', u'than', u'versus', u'vs', u'vs.', u'distinct', 'over', 'contrast']:
						for child in children:
							if child.lemma_ in interv + patients:
								comparison_found = True
							else:
								for child_child in child.children:
									if child_child.lemma_ in interv + patients:
										comparison_found = True


					elif token.text.lower() in ['superior', 'inferior']: #, 'more', 'less']:
						comparison_found = True

					elif token.lemma_ in [u'may', u'can', u'will', u'could', u'would', 'might', u'whether', u'expect', u'objective', 'aim', u'hypothesis', 'hypothesize', 'fail']:
						modal_beg = token.i
						modal_found = True

					elif token.lemma_ in ['associate']:
						assoc_beg = token.i
						assoc_found = True

					elif token.lemma_ in ['proportion']:
						for child in children:
							if child.lemma_ == 'of':
								for child_child in child.children:
									if child_child.lemma_ in patients:
										proportion_found = True

					elif token.lemma_ in ['evaluate', 'assess']:
						for child in children:
							if child.lemma_ in ['to', 'be']:
								assess_beg = token.i
								assess_found = True	

					elif token.lemma_ in ['outcome']:
						if token.head.lemma_ == 'be':
							modal_beg = token.i
							modal_found = True

				if wgc_word_found and (not comparison_found) and (not proportion_found) and ((not assoc_found) or (assoc_found and assoc_beg > wgc_ind)) and ((not modal_found) or (modal_found and modal_beg > wgc_ind)) and (not assess_found):
					results.add(('WGC', wgc_ind, wgc_ind, sent_id, '', 0))


			#print("Sentence {0} out of {1} ".format(sent_id, len(self.sentences)))

		return results							
		

	def find_rec(self, parser = 'spacy'):

		print("Searching for recommentations")

		#self.unescape_xml()
		text = self.text
		pattern = re.compile('([a-z]{4,}([aoi][nl]e|[aoi]n|[oi]l)\\b|\\bp\\b|achieve|across|act|activ|addition|additional|adjunct|admit|administration|adolescent|adult|advise|aftercare|agent|aim|all|alternative|ameliorat|among|analysis|analyze|antidepressant|antipsychotic|appear|approach|appropriate|arm|article|assess|associat|avenue|baseline|battery|beneficial|benefit|better|between|between-group|both|burden|candidate|chang|child|choice|CI|cohort|compar|complet|compris|concern|conduct|confidence|consider|consist|constitut|contribution|control|core|correlat|cover|criteri|day|decade|declin|decreas|defin|demonstrat|design|desirable|determin|differen|display|dos|drug|each|effect|efficac|either|elevat|emerge|end|enhanc|enrol|equal|equivalen|estimat|evaluat|event|evolv|examin|excellent|exhibit|faster|favor|favour|feasible|female|final|find|first|follow|formulation|fulfil|gain|giv|goal|good|greater|group|have|higher|hour|hypothesis|hypothesiz|identical|impact|important|improv|incidence|includ|increas|incur|indicat|individual|induc|infant|inferior|inferiority|influenc|innovative|instrument|intent|interesting|interval|intervention|introduc|investigat|investigation|involv|key|less|level|limit|lower|main|major|mak|male|man|margin|mean|measur|medication|medicine|meet|methodology|month|more|neonate|neuroleptic|new|newborn|non-inferior|noninferior|novel|objective|observ|occur|offer|option|outcome|p-value|parameter|parent|part|participant|participat|patient|people|perform|period|person|phenotype|placebo|point|poorer|population|possible|poten|potency|potential|powerful|pre-\S+|prefer|present|primary|principal|produc|project|promis|protocol|prov|purpose|pvalue|quicker|random|rank|rat|reach|receiv|recommend|reduc|regular|relat|report|represent|research|respond|respondent|response|result|review|safe|same|sample|satisf|scale|schizophren|shorter|score|screen|second|secondary|see|seem|sensible|serv|show|significan|similar|slower|specif|stand|strateg|stud|subgroup|subject|subsidiary|substitut|successful|suggest|suit|support|survey|symptom|tak|target|term|test|than|therapy|time|toler|tolerab|tolerated|tool|total|treat|trial|type|useful|valid|valuable|value|variable|versus|viable|visit|vs|we|week|withdrawal|woman|work|worse|year|yield)', re.IGNORECASE)

		if self.sentences == []:
			self.sent_split()
			
		if self.abstract == None:
			self.find_abstract()

		if self.results != None and self.conclusions != None:
			beg_search = self.results[1]
			end_search = self.conclusions[2]
		elif self.results != None and self.conclusions == None:
			beg_search = self.results[1]
			end_search = self.results[2]
		elif self.results == None and self.conclusions != None:
			beg_search = self.conclusions[1]
			end_search = self.conclusions[2]
		elif self.results == None and self.conclusions == None:
			beg_search = self.abstract[1]
			end_search = self.abstract[2]

		# find sentence numbers for abstract
		abstr_sent = []
		sent_id = 0
		for sent in self.sentences:
			sent_beg = sent[1]
			sent_end = sent[2]
			if sent_beg <= beg_search and sent_end > beg_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_end <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			elif sent_beg >= beg_search and sent_beg <= end_search:
				abstr_sent.append(self.sentences[sent_id] + (sent_id, ))
			sent_id += 1


		results = set()
		for sent in abstr_sent:
			sent_text = sent[0]
			sent_beg = sent[1]
			sent_end = sent[2]
			sent_id = sent[3] #self.sentences.index(sent)
			if pattern.search(sent_text):
				if (sent_id, parser) not in self.sentences_depparsed.keys():
					sent_tagged, sent_depparsed = self.depparse_sent(depparser = parser, sentence = sent_text)
					self.sentences_depparsed[(sent_id, parser)] = sent_depparsed
					self.sentences_tagged[(sent_id, parser)] = sent_tagged

				tags = self.sentences_tagged[(sent_id, parser)]

				tokens = []
				text_tagged = []
				num = 0
				for item in tags:
					text_tagged.append((item[0], item[1], item[2], num))
					tokens.append(item[0])
					num = num + 1


				#Find Components + positions

				for item in text_tagged:
					num = text_tagged.index(item)
								

					# recommendations
					if check_token(num, text_tagged, lemma_list = [u'useful']):
						i = num

						if check_left(i, text_tagged, pos_list = ['RB', 'RBS', 'RBR']):
							i = i - 1

						if check_left(i, text_tagged, lemma_list = [u'as', u'among']):
							i = i - 1

						if check_left(i, text_tagged, pos_list = ['NN', 'NNS', 'NP', 'NPS']):
							i = i - 1
				
							
						if check_left(i, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise', u'prove', u'support', u'favor', u'favour', u'introduce']):
							results.add(('Rec', i - 1, num, sent_id, '', 0))


						k = num
						if check_left(k, text_tagged, pos_list = ['DT']):
							k = k - 1

						if check_left(k, text_tagged, lemma_list = [u'be']):
							k = k - 1

							if check_left(k, text_tagged, pos_list = ['RB', 'RBS', 'RBR']):
								k = k - 1	

							if check_left(k, text_tagged, lemma_list = [u'can', u'may'], pos_list = ['MD']):
								k = k - 1
								results.add(('Rec', k - 1, num, sent_id, '', 0))


					if check_token(num, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise', u'prove', u'support', u'favor', u'favour', u'introduce']):
						i = num

						if check_right(i, text_tagged, pos_list = ['NN', 'NNS', 'NP', 'NPS']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'as', u'among']):
							i = i + 1


						while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'CD', 'PP$', 'DT', 'PDT', 'NN', 'NNS', 'NP', 'NPS', 'NN+POS', 'NNS+POS', 'NP+POS', 'NPS+POS', 'VVG', 'VVN'], pos_not_list = ['SENT'], lemma_not_list = ['new', 'alternative', 'addition', 'additional', 'active', 'useful', 'suitable', 'valuable', 'effective', 'efficacious', 'safe', 'possible', 'promising', 'desirable', 'viable', 'interesting', 'important', 'prefer', 'recommend', 'preferred', 'recommended', 'powerful', 'successful', 'appropriate', 'well-tolerated', 'tolerated', 'feasible', 'excellent', 'beneficial', 'regular', 'innovative', 'potential', 'sensible', 'novel', 'valid', 'good', 'more', 'less', 'choice', 'drug', 'medication', 'controller', 'treatment', 'agent', 'therapy', 'medicine', 'intervention']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'drug', u'medication', u'controller', u'treatment', u'agent', u'therapy', u'medicine', u'intervention']):
							i = i + 1
							if check_right(i, text_tagged, lemma_list = [u'option']):
								results.add(('Rec', num, i + 1, sent_id, '', 0))
							elif check_right(i, text_tagged, lemma_list = [u'of']):
								i = i + 1
								if check_right(i, text_tagged, lemma_list = [u'choice']):
									results.add(('Rec', num, i + 1, sent_id, '', 0))
								if check_right(i, text_tagged, lemma_list = [u'first']):
									if check_right(i + 1, text_tagged, lemma_list = [u'choice']):
										results.add(('Rec', num, i + 2, sent_id, '', 0))
						
						elif check_right(i, text_tagged, lemma_list = [u'new', u'alternative', u'addition', u'additional', u'active', u'useful', u'suitable', u'valuable', u'effective', u'efficacious', u'safe', u'possible', u'promising', u'desirable', u'viable', u'interesting', u'important', u'prefer', u'recommend', u'preferred', u'recommended', u'powerful', u'successful', u'appropriate', u'well-tolerated', u'tolerated', u'feasible', u'excellent', u'beneficial', u'regular', u'innovative', u'potential', u'sensible', u'novel', u'valid', u'good', u'more', u'less', u'choice']):
							i = i + 1
							if check_right(i, text_tagged, lemma_list = [u'and']):
								if check_right(i + 1, text_tagged, lemma_list = [u'new', u'alternative', u'addition', u'additional', u'active', u'useful', u'suitable', u'valuable', u'effective', u'efficacious', u'safe', u'possible', u'promising', u'desirable', u'viable', u'interesting', u'important', u'prefer', u'recommend', u'preferred', u'recommended', u'powerful', u'successful', u'appropriate', u'well-tolerated', u'tolerated', u'feasible', u'excellent', u'beneficial', u'regular', u'innovative', u'potential', u'sensible', u'novel', u'valid', u'good', u'more', u'less', u'choice']):
									i = i + 2

							if check_right(i, text_tagged, lemma_list = [u'as']):
								i = i + 1

							while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'CD', 'PP$', 'DT', 'PDT', 'NN', 'NNS', 'NP', 'NPS', 'NN+POS', 'NNS+POS', 'NP+POS', 'NPS+POS', 'VVG', 'VVN'], pos_not_list = ['SENT'], lemma_not_list = ['option', 'alternative', 'choice', 'approach', 'candidate', 'drug', 'medication', 'controller', 'treatment', 'tool', 'substitute', 'agent', 'avenue', 'adjunct', 'strategy', 'therapy', 'medicine', 'intervention', 'neuroleptic']):
								i = i + 1

							if check_right(i, text_tagged, lemma_list = [u'option', u'alternative', u'choice', u'approach', u'candidate', u'drug', u'medication', u'controller', u'treatment', u'tool', u'substitute', u'agent', u'avenue', u'adjunct', u'strategy', u'therapy', u'medicine', u'intervention', u'neuroleptic']):
								i = i + 1
								results.add(('Rec', num, i, sent_id, '', 0))
				

					if check_token(num, text_tagged, lemma_list = [u'drug', u'medication', u'controller', u'treatment', u'agent', u'therapy', u'medicine', u'intervention', u'neuroleptic', u'formulation']):
						i = num
						while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHG', 'VHN', 'VHP', 'VHZ', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ'], pos_not_list = ['SENT'], lemma_not_list = ['be', 'seem', 'appear', 'provide', 'give', 'serve', 'consider', 'suggest', 'constitute', 'represent', 'present', 'offer', 'evolve', 'emerge', 'stand', 'rank', 'recommend', 'advise']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'to']):
							if check_right(i + 1, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise']):
								i = i + 2

						if check_right(i, text_tagged, lemma_list = [u'as']):
							i = i + 1

						while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'CD', 'PP$', 'DT', 'PDT', 'NN', 'NNS', 'NP', 'NPS', 'NN+POS', 'NNS+POS', 'NP+POS', 'NPS+POS', 'VVG', 'VVN'], lemma_list = [u'and'], pos_not_list = ['SENT'], lemma_not_list = ['alternative', u'active', u'useful', u'suitable', u'valuable', u'promising', u'desirable', u'viable', u'prefer', u'recommend', u'preferred', u'recommended', u'powerful', u'successful', u'appropriate' 'feasible', u'innovative', u'potential', u'sensible', u'novel', u'valid']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'alternative', u'active', u'useful', u'suitable', u'valuable', u'promising', u'desirable', u'viable', u'prefer', u'recommend', u'preferred', u'recommended', u'powerful', u'successful', u'appropriate' 'feasible', u'innovative', u'potential', u'sensible', u'novel', u'valid']):
							results.add(('Rec', num, i + 1, sent_id, '', 0))
	



					if check_token(num, text_tagged, lemma_list = [u'option', u'alternative', u'choice', u'approach', u'candidate', u'tool', u'substitute', u'avenue', u'adjunct', u'strategy', u'option', u'approach']):
						i = num
						while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHG', 'VHN', 'VHP', 'VHZ', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ'], pos_not_list = ['SENT'], lemma_not_list = ['be', 'seem', 'appear', 'provide', 'give', 'serve', 'consider', 'suggest', 'constitute', 'represent', 'present', 'offer', 'evolve', 'emerge', 'stand', 'rank', 'recommend', 'advise']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'to']):
							if check_right(i + 1, text_tagged, lemma_list = [u'be', u'seem', u'appear', u'provide', u'give', u'serve', u'consider', u'suggest', u'constitute', u'represent', u'present', u'offer', u'evolve', u'emerge', u'stand', u'rank', u'recommend', u'advise']):
								i = i + 2

						if check_right(i, text_tagged, lemma_list = [u'as']):
							i = i + 1

						while i < len(text_tagged) and check_right(i, text_tagged, pos_list = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'CD', 'PP$', 'DT', 'PDT', 'NN', 'NNS', 'NP', 'NPS', 'NN+POS', 'NNS+POS', 'NP+POS', 'NPS+POS', 'VVG', 'VVN'], lemma_list = [u'and'], pos_not_list = ['SENT'], lemma_not_list = ['new', u'alternative', u'first', u'additional', u'addition', u'useful', u'suitable', u'valuable', u'effective', u'efficacious', u'safe', u'promising', u'desirable', u'viable', u'interesting', u'important', u'prefer', u'recommend', u'powerful', u'successful', u'appropriate', u'well-tolerated', u'tolerated', u'feasible', u'excellent', u'beneficial', u'regular', u'innovative', u'potential', u'sensible', u'novel', u'valid']):
							i = i + 1

						if check_right(i, text_tagged, lemma_list = [u'new', u'alternative', u'first', u'additional', u'addition', u'useful', u'suitable', u'valuable', u'effective', u'efficacious', u'safe', u'promising', u'desirable', u'viable', u'interesting', u'important', u'prefer', u'recommend', u'powerful', u'successful', u'appropriate', u'well-tolerated', u'tolerated', u'feasible', u'excellent', u'beneficial', u'regular', u'innovative', u'potential', u'sensible', u'novel', u'valid']):
							results.add(('Rec', num, i + 1, sent_id, '', 0))

			print("Sentence {0} out of {1} ".format(sent_id, len(self.sentences)))
		return results

		# end preannotation for evaluations


	def find_po(self, parser = 'bert'):
		# find the primary outcome among declared outcomes
		# compare PO in abstract to PO in body text
		#print("Searching for pre-defined primary outcomes")

		PO_list = set()
		PO_abstr_list = set()
		PO_bt_list = set()
		
		SO_list = set()
		SO_abstr_list = set()
		SO_bt_list = set()

		out_abstr = []
		out_bt = []

		# if there are no declared outcomes, search for them
		if self.outcomes_declared == None:
			#self.preannot_po()
			#self.preannot_po_synt('spacy')
			#self.preannot_outcomes_bert()
			self.preannot_po_biobert()
		
		# if there are still no declared outcomes, they canot be found
		if len(self.outcomes_declared) == 0:
			print("Pre-defined outcomes not found in the text!")
		else:
			# filter outcomes found		
			outcomes_declared_filtered = advanced_filter_preannot_results(self.outcomes_declared)

			#find abstractadvanced_filter_preannot_results
			if self.abstract == None:
				self.find_abstract()

			# if abstract not found, all outcomes are body text outcomes
			if self.abstract == '':
				if len(outcomes_declared_filtered) == 1:
					out = outcomes_declared_filtered[0]
					sent_id = out[3]
					out_sent = self.sentences_tagged[(sent_id, parser)]
					out_sent_text = [ item[0] for item in out_sent ]
					out_str = ' '.join(out_sent_text[out[1] : out[2] + 1])
					if out[4] == 'Type="None" Status="Declared"' or out[4] == 'Type="Prim" Status="Declared"':
						PO_list.add((out_str, ) + out)
					elif out[4] == 'Type="Sec" Status="Declared"':
						SO_list.add((out_str, ) + out)
				else:
					for out in outcomes_declared_filtered:
						sent_id = out[3]
						out_sent = self.sentences_tagged[(sent_id, parser)]
						out_sent_text = [ item[0] for item in out_sent ]
						out_str = ' '.join(out_sent_text[out[1] : out[2] + 1])
						if out[4] == 'Type="Prim" Status="Declared"':
							PO_list.add( (out_str, ) + out)
						elif out[4] == 'Type="Sec" Status="Declared"':
							SO_list.add( (out_str, ) + out)

			else:
				abstr_beg = self.abstract[1]
				abstr_end = self.abstract[2]

				#print(abstr_beg, abstr_end)

				for out in outcomes_declared_filtered:
					sent_id = out[3]
					out_sent = self.sentences_tagged[(sent_id, parser)]
					out_sent_text = [ item[0] for item in out_sent ]
					sent_beg = self.sentences[sent_id][1]
					out_beg = sent_beg + out_sent[out[1]][3]
					out_end = sent_beg + out_sent[out[2]][4]

					out_str = ' '.join(out_sent_text[out[1] : out[2] + 1])
		
					if out_beg >= abstr_beg and out_end <= abstr_end:
						#print((out_str, ) + out)
						out_abstr.append((out_str, ) + out)
					elif out_beg > abstr_end:
						out_bt.append((out_str, ) + out)

				# find POs

				# if there in only one outcome with type none or prim, it is primary
				# search separately in abstract and in body text

				if len(out_abstr) == 1:
					if out_abstr[0][5] == 'Type="None" Status="Declared"' or out_abstr[0][5] == 'Type="Prim" Status="Declared"':
						PO_abstr_list.add(out_abstr[0])
						PO_list.add(out_abstr[0])
						
					elif out_abstr[0][5] == 'Type="Sec" Status="Declared"':
						SO_abstr_list.add(out_abstr[0])
						SO_list.add(out_abstr[0])
				else:
					for out in out_abstr:
						if out[5] == 'Type="Prim" Status="Declared"':
							PO_list.add(out)
							PO_abstr_list.add(out)
							
						elif out[5] == 'Type="Sec" Status="Declared"':
							SO_list.add(out)
							SO_abstr_list.add(out)
							
				if len(out_bt) == 1:
					if out_bt[0][5] == 'Type="None" Status="Declared"' or out_bt[0][5] == 'Type="Prim" Status="Declared"':
						PO_bt_list.add(out_bt[0])
						PO_list.add(out_bt[0])
					
					elif out_bt[0][5] == 'Type="Sec" Status="Declared"':
						SO_bt_list.add(out_bt[0])
						SO_list.add(out_bt[0])
				else:
					for out in out_bt:
						if out[5] == 'Type="Prim" Status="Declared"':
							PO_list.add(out)
							PO_bt_list.add(out)
						if out[5] == 'Type="Sec" Status="Declared"':
							SO_list.add(out)
							SO_bt_list.add(out)
	

		if len(PO_list) == 0:
			print('No pre-defined primary outcomes were found!')

		self.PO_list = list(PO_list)
		self.PO_abstr_list = list(PO_abstr_list)
		self.PO_bt_list = list(PO_bt_list)

		self.SO_list = list(SO_list)
		self.SO_abstr_list = list(SO_abstr_list)
		self.SO_bt_list = list(SO_bt_list)
		
		if DEBUG: print(self.PO_list)
		if DEBUG: print(self.PO_abstr_list)
		if DEBUG: print(self.PO_bt_list)


	def find_out_variants(self, out_list):
		print("Searching for outcome variants")
		out_measures = {}
		out_short = {}
		out_disabbr = {}

		if self.abbreviations == None:
			self.find_abbr()

		meas_reg = re.compile('(.*)\s*,?\s*(?:as|which \w+|that \w+)? (?:measured|assessed|defined|rated|quantified|marked|tested|recorded) (?:with|by|as|using|on|through) (.*)')

		for out in out_list:
			out_str = out
			if DEBUG: print(out_str)

			out_rep = out_str
			for abbr in self.abbr_dict.keys():
				if out_rep.find(abbr) != -1:
					out_rep = out_rep.replace(abbr, self.abbr_dict[abbr])

			if out_rep != out_str:
				out_disabbr[out_str] = out_rep
			
			if out_str in out_disabbr.keys():
				meas_match = meas_reg.match(out_disabbr[out_str])
			else:
				meas_match = meas_reg.match(out_str)

			if meas_match:
				out_new = meas_match.group(1)

				meas = meas_match.group(2)
				if DEBUG: print(out_new, meas)

				out_measures[out_str] = meas
				out_short[out_str] = out_new

		if DEBUG: print(out_measures, out_short, out_disabbr)
		return out_measures, out_short, out_disabbr


	def find_out_rep_abstr(self, parser = 'bert'):
##		print("Searching for reported outcomes in the abstract")
		out_rep_abstr_list = []
		if self.outcomes_reported == None:
			#self.preannot_reported_outcomes()
			#self.preannot_rep_out_synt('spacy')
			#self.preannot_outcomes_bert()
			self.preannot_rep_scibert()

		if len(self.outcomes_reported) == 0:
			print('No reported outcomes found in the text!')
		else:
			outcomes_reported_filtered = advanced_filter_preannot_results(self.outcomes_reported)

			if self.abstract == None:
				self.find_abstract()

			if self.results != None and self.conclusions != None:
				beg_search = self.results[1]
				end_search = self.conclusions[2]
			elif self.results != None and self.conclusions == None:
				beg_search = self.results[1]
				end_search = self.results[2]
			elif self.results == None and self.conclusions != None:
				beg_search = self.conclusions[1]
				end_search = self.conclusions[2]
			elif self.results == None and self.conclusions == None:
				beg_search = self.abstract[1]
				end_search = self.abstract[2]

			for item in outcomes_reported_filtered:
				if item[0] == 'Out':
					sent_id = item[3]
					out_sent = self.sentences_tagged[(sent_id, parser)]
					out_sent_text = [ tok[0] for tok in out_sent ]
					sent_beg = self.sentences[sent_id][1]
					out_beg = sent_beg + out_sent[item[1]][3]
					out_end = sent_beg + out_sent[item[2]][4]

					out_str = ' '.join(out_sent_text[item[1] : item[2] + 1])

					if out_beg >= beg_search and out_end <= end_search:
						out_rep_abstr_list.append( (out_str, ) + item)


		self.out_rep_abstr = out_rep_abstr_list


	def compare_outcomes_bert(self, out_list1, out_list2):
		print("Comparing outcomes")
		if DEBUG: print(out_list1)
		if DEBUG: print(out_list2)
		compare_res = {}
		bert_input = []

		for out1 in out_list1:
			for out2 in out_list2:
				# make input for bert
				bert_input.append((out1, out2))

		if len(bert_input) == 0: print('ERROR empty input for BERT')

		results, labels = run_classifier.main(bert_input, 'sim')
		for (i, probabilities) in enumerate(results):
			if probabilities[1] > probabilities[0]:
				compare_res[bert_input[i]] = True
			else:
				compare_res[bert_input[i]] = False

		os.remove("tmp/predict.tf_record")

		print(compare_res)
		return compare_res


	def compare_outcomes_with_variants_bert(self, out_list1, out_list2):
		print("Comparing outcomes")
		if DEBUG: print(out_list1)
		if DEBUG: print(out_list2)
		compare_res = {}

		variants1 = self.find_out_variants(out_list1)
		variants2 = self.find_out_variants(out_list2)
		#print(out_list1)
		#print(out_list2)
		#print(variants1)
		#print(variants2)

		measures1 = variants1[0]
		short1 = variants1[1]
		disabbr1 = variants1[2]

		measures2 = variants2[0]
		short2 = variants2[1]
		disabbr2 = variants2[2]

		for out1 in out_list1:
			bert_input = []

			out_with_var1 = [ out1 ]
			if out1 in disabbr1.keys():
				out_disabbr1 = disabbr1[out1]
				out_with_var1.append(out_disabbr1)

			if out1 in measures1.keys():
				out_measure1 = measures1[out1]
				out_with_var1.append(out_measure1)

			if out1 in short1.keys():
				out_short1 =short1[out1]
				out_with_var1.append(out_short1)

			for out2 in out_list2:
				out_with_var2 = [ out2 ]
				if out2 in disabbr2.keys():
					out_disabbr2 = disabbr2[out2]
					out_with_var2.append(out_disabbr2)

				if out2 in measures2.keys():
					out_measure2 = measures2[out2]
					out_with_var2.append(out_measure2)

				if out2 in short2.keys():
					out_short2 =short2[out2]
					out_with_var2.append(out_short2)

				# make input for bert
				for item1 in out_with_var1:
					for item2 in out_with_var2:
						bert_input.append((item1, item2))

				if len(bert_input) == 0: print('ERROR empty input for BERT')

				results, labels = run_classifier.main(bert_input, 'sim')
				for probabilities in results:
					if probabilities[1] > 0.5:
						compare_res[(out1, out2)] = True
						break
				if (out1, out2) not in compare_res.keys():
					compare_res[(out1, out2)] = False

				os.remove("tmp/predict.tf_record")

		#print(compare_res)
		return compare_res
	

	def compare_po_abstr_bt(self, parser = 'bert'):
		meta = ''
		print("Comparing primary outcomes in the abstract and in the body")
		matching_outcomes = []
		outcomes_not_matched = set()
		if self.PO_list == None:
			self.find_po()

		out_abstr_matched = set()
		out_bt_matched = set()

		if len(self.PO_abstr_list) == 0:
			print("There are no declared outcomes in the abstract.")
			meta = "There are no declared outcomes in the abstract.\n"

		elif len(self.PO_bt_list) == 0:
			print("There are no declared outcomes in the body.")
			meta = "There are no declared outcomes in the body.\n"

		else:
			po_abstr_list = [ out[0] for out in self.PO_abstr_list ]
			#print(po_abstr_list)

			po_bt_list = [ out[0] for out in self.PO_bt_list ]
			#print(po_bt_list)

			#comparison = self.compare_outcomes_with_variants(po_abstr_list, po_bt_list)
			comparison = self.compare_outcomes_bert(po_abstr_list, po_bt_list)
			
			for key in comparison.keys():
				if comparison[key]:
					out1 = key[0]
					out2 = key[1]

					out1_beg_tok = self.PO_abstr_list[po_abstr_list.index(out1)][2]
					out1_end_tok = self.PO_abstr_list[po_abstr_list.index(out1)][3]
					out1_sent_id = self.PO_abstr_list[po_abstr_list.index(out1)][4]	
					out1_sent = self.sentences_tagged[(out1_sent_id, parser)]
					sent1_beg = self.sentences[out1_sent_id][1]
					out1_beg = sent1_beg + out1_sent[out1_beg_tok][3]
					out1_end = sent1_beg + out1_sent[out1_end_tok][4]


					out2_beg_tok = self.PO_bt_list[po_bt_list.index(out2)][2]
					out2_end_tok = self.PO_bt_list[po_bt_list.index(out2)][3]
					out2_sent_id = self.PO_bt_list[po_bt_list.index(out2)][4]	
					out2_sent = self.sentences_tagged[(out2_sent_id, parser)]
					sent2_beg = self.sentences[out2_sent_id][1]
					out2_beg = sent2_beg + out2_sent[out2_beg_tok][3]
					out2_end = sent2_beg + out2_sent[out2_end_tok][4]

					matching_outcomes.append((out1, out2, out1_beg, out1_end, out2_beg, out2_end, out2_sent_id))
					out_abstr_matched.add(out1)
					out_bt_matched.add(out2)


			out_not_matched_abstr = set(po_abstr_list) - out_abstr_matched
			out_not_matched_bt = set(po_bt_list) - out_bt_matched

			for out in (out_not_matched_abstr ):
				out_beg_tok = self.PO_abstr_list[po_abstr_list.index(out)][2]
				out_end_tok = self.PO_abstr_list[po_abstr_list.index(out)][3]
				out_sent_id = self.PO_abstr_list[po_abstr_list.index(out)][4]	
				out_sent = self.sentences_tagged[(out_sent_id, parser)]
				sent_beg = self.sentences[out_sent_id][1]
				out_beg = sent_beg + out_sent[out_beg_tok][3]
				out_end = sent_beg + out_sent[out_end_tok][4]

				outcomes_not_matched.add((out, out_beg, out_end))

			for out in (out_not_matched_bt ):
				out_beg_tok = self.PO_bt_list[po_bt_list.index(out)][2]
				out_end_tok = self.PO_bt_list[po_bt_list.index(out)][3]
				out_sent_id = self.PO_bt_list[po_bt_list.index(out)][4]	
				out_sent = self.sentences_tagged[(out_sent_id, parser)]
				sent_beg = self.sentences[out_sent_id][1]
				out_beg = sent_beg + out_sent[out_beg_tok][3]
				out_end = sent_beg + out_sent[out_end_tok][4]

				outcomes_not_matched.add((out, out_beg, out_end))


			if len(matching_outcomes) != 0:
				col_width = max(len(phrase) for row in matching_outcomes for phrase in [row[0], row[1]]) + 5  # padding
				print("The list of corresponding outcomes from the abstract and the body:")
				meta = meta + "The list of corresponding outcomes from the abstract and the body:\n"
				col_names = "".join(['Abstract'.ljust(col_width), 'Body'.ljust(col_width)])
				#print(col_names)
				meta += col_names + "\n"
				for item in matching_outcomes:
					pair = "".join([item[0].ljust(col_width), item[1].ljust(col_width)])
					#print(pair)
					meta = meta + pair + '\n'


			if len(out_not_matched_abstr) != 0:
				print("There is no corresponding outcomes in the body for the following outcomes from the abstract: ", out_not_matched_abstr )
				meta += "There is no corresponding outcomes in the body for the following outcomes from the abstract:\n"
				for out in out_not_matched_abstr:
					meta += out[0] + '\n'
			else:
				print("For each primary outcome in the abstract there is a corresponding primary outcome in the body.")
				meta += "For each primary outcome in the abstract there is a corresponding primary outcome in the body.\n"

			if len(out_not_matched_bt) != 0:
				print("There is no corresponding outcomes in the abstract for the following outcomes from the body: ", out_not_matched_bt )
				meta = meta + "There is no corresponding outcomes in the abstract for the following outcomes from the body:\n"
				for out in out_not_matched_bt:
					meta += out[0] + '\n'
			else:
				print("For each primary outcome in the body there is a corresponding primary outcome in the abstract.")
				meta += "For each primary outcome in the body there is a corresponding primary outcome in the abstract.\n"

		return matching_outcomes, outcomes_not_matched, meta
		
		
	def compare_po_text_registry(self, parser = 'bert'):
		meta = ''
		print("Comparing primary outcomes in the registry and in the text of the article")
		matching_outcomes = []
		outcomes_not_matched = set()

		if self.registry_parsed == None:
			self.parse_all_registries()

		if len(self.registry_parsed) == 0:
			print("There is no corresponding registry entry found.")
			meta = "There is no corresponding registry entry found.\n"

		else:
			if self.PO_list == None:
				self.find_po()

			out_text_matched = set()
			out_reg_matched = set()

			if len(self.PO_list) == 0:
####				print("There are no declared outcomes in the text.")
				meta = "There are no declared outcomes in the text.\n"
			
			else:
				meta += 'Primary outcomes from the text:\n'
				for po in self.PO_list:
					meta += po[0] + '\n'

				outcome_reg = re.compile("primary\s(outcome|end[ -]?point)", re.IGNORECASE)
				time_reg = re.compile("time", re.IGNORECASE)

				registry_outcomes = set()				

				for item in self.registry_parsed:
					parse_results = eval(item[2])
					for key in parse_results.keys():
						if outcome_reg.search(key):
							if not time_reg.search(key):
								value = [ item for item in parse_results[key] if (item != '' and not re.match('\[Time Frame: .*?\]', item) ) ]
								registry_outcomes = registry_outcomes | set(value)

				if len(registry_outcomes) == 0:
					print("No primary outcomes found in the registry entry.")
					meta = "No primary outcomes found in the registry entry.\n"
				else:
					meta += 'Primary outcomes from trial registry:\n'
					for reg_out in registry_outcomes:
						meta += reg_out + '\n'

					po_list = [ out[0] for out in self.PO_list ]

					#comparison = self.compare_outcomes_with_variants(registry_outcomes, po_list)
					comparison = self.compare_outcomes_bert(registry_outcomes, po_list)
			
					for key in comparison.keys():
						if comparison[key]:
							out1 = key[0]
							out2 = key[1]

							out2_beg_tok = self.PO_list[po_list.index(out2)][2]
							out2_end_tok = self.PO_list[po_list.index(out2)][3]
							out2_sent_id = self.PO_list[po_list.index(out2)][4]	
							out2_sent = self.sentences_tagged[(out2_sent_id, parser)]
							sent2_beg = self.sentences[out2_sent_id][1]
							out2_beg = sent2_beg + out2_sent[out2_beg_tok][3]
							out2_end = sent2_beg + out2_sent[out2_end_tok][4]

							matching_outcomes.append((out1, out2, out2_beg, out2_end, out2_sent_id))
							out_reg_matched.add(out1)
							out_text_matched.add(out2)

					out_not_matched_reg = set(registry_outcomes) - out_reg_matched
					out_not_matched_text = set(po_list) - out_text_matched


					for out in (out_not_matched_text):
						out_beg_tok = self.PO_list[po_list.index(out)][2]
						out_end_tok = self.PO_list[po_list.index(out)][3]
						out_sent_id = self.PO_list[po_list.index(out)][4]	
						out_sent = self.sentences_tagged[(out_sent_id, parser)]
						sent_beg = self.sentences[out_sent_id][1]
						out_beg = sent_beg + out_sent[out_beg_tok][3]
						out_end = sent_beg + out_sent[out_end_tok][4]

						outcomes_not_matched.add((out, out_beg, out_end))


					if len(matching_outcomes) != 0:
						col_width = max(len(phrase) for row in matching_outcomes for phrase in [row[0], row[1]]) + 5  # padding
						print("The list of corresponding outcomes from the registry and the text:")
						meta = meta + "The list of corresponding outcomes from the registry and the text:\n"
						col_names = "".join(['Registry'.ljust(col_width), 'Text'.ljust(col_width)])
						#print(col_names)
						meta += col_names + "\n"
						for item in matching_outcomes:
							pair = "".join([item[0].ljust(col_width), item[1].ljust(col_width)])
							#print(pair)
							meta += pair + '\n'

					if len(out_not_matched_reg) != 0:
						print("There is no corresponding outcomes in the text for the following outcomes from the registry: ", out_not_matched_reg )
						meta = meta + "There is no corresponding outcomes in the text for the following outcomes from the registry:\n"
						for out in out_not_matched_reg:
							meta += out + '\n'

					else:
						print("All primary outcomes from the registry are present among the primary outcomes of the text.")
						meta = meta + "All primary outcomes from the registry are present among the primary outcomes of the text.\n"

					if len(out_not_matched_text) != 0:
						print("There is no corresponding outcomes in the registry for the following outcomes from the text: ", out_not_matched_text )
						meta = meta + "There is no corresponding outcomes in the registry for the following outcomes from the text:\n"
						for out in out_not_matched_text:
							meta += out + '\n'

					else:
						print("All primary outcomes of the text are present among the primary outcomes of the registry.")
						meta = meta + "All primary outcomes of the text are present among the primary outcomes of the registry.\n"
		

		return matching_outcomes, outcomes_not_matched, meta


	def compare_po_rep(self, parser = 'bert'):
		meta = ''
		print("Comparing primary outcomes and outcomes reported in the abstract")
		matching_outcomes = []
		outcomes_not_matched = set()
		if self.PO_list == None:
			self.find_po()

		out_matched = set()

		if len(self.PO_list) == 0:
##			print("There are no declared primary outcomes in the text.")
			meta = "There are no declared primary outcomes in the text.\n"
			
		else:
			po_list = [ out[0] for out in self.PO_list ]

			self.find_out_rep_abstr()
			out_rep_list = [ out[0] for out in self.out_rep_abstr ]

			#comparison = self.compare_outcomes_with_variants(po_list, out_rep_list)
			comparison = self.compare_outcomes_bert(po_list, out_rep_list)
			
			for key in comparison.keys():
				if comparison[key]:
					out1 = key[0]
					out2 = key[1]

					out1_beg_tok = self.PO_list[po_list.index(out1)][2]
					out1_end_tok = self.PO_list[po_list.index(out1)][3]
					out1_sent_id = self.PO_list[po_list.index(out1)][4]	
					out1_sent = self.sentences_tagged[(out1_sent_id, parser)]
					sent1_beg = self.sentences[out1_sent_id][1]
					out1_beg = sent1_beg + out1_sent[out1_beg_tok][3]
					out1_end = sent1_beg + out1_sent[out1_end_tok][4]


					out2_beg_tok = self.out_rep_abstr[out_rep_list.index(out2)][2]
					out2_end_tok = self.out_rep_abstr[out_rep_list.index(out2)][3]
					out2_sent_id = self.out_rep_abstr[out_rep_list.index(out2)][4]	
					out2_sent = self.sentences_tagged[(out2_sent_id, parser)]
					sent2_beg = self.sentences[out2_sent_id][1]
					out2_beg = sent2_beg + out2_sent[out2_beg_tok][3]
					out2_end = sent2_beg + out2_sent[out2_end_tok][4]


					matching_outcomes.append((out1, out2, out1_beg, out1_end, out2_beg, out2_end, out2_sent_id))
					out_matched.add(out1)


			"""out_not_matched = set(po_list) - out_matched
			if len(out_not_matched) != 0:
				self.find_np_abstr()
				np_abstr_list = [ np[0] for np in self.np_abstr if np not in out_rep_list ]
				comparison = self.compare_outcomes_with_variants(list(out_not_matched), np_abstr_list)

				for key in comparison:
					if comparison[key]:
						out1 = key[0]
						np = key[1]
					
						out1_beg_tok = self.PO_list[po_list.index(out1)][2]
						out1_end_tok = self.PO_list[po_list.index(out1)][3]
						out1_sent_id = self.PO_list[po_list.index(out1)][4]	
						out1_sent = self.sentences_tagged[(out1_sent_id, parser)]
						sent1_beg = self.sentences[out1_sent_id][1]
						out1_beg = sent1_beg + out1_sent[out1_beg_tok][3]
						out1_end = sent1_beg + out1_sent[out1_end_tok][4]

						np_beg_tok = self.np_abstr[np_abstr_list.index(np)][1]
						np_end_tok = self.np_abstr[np_abstr_list.index(np)][2]
						np_sent_id = self.np_abstr[np_abstr_list.index(np)][3]	
						np_sent = self.sentences_tagged[(np_sent_id, parser)]
						sent2_beg = self.sentences[np_sent_id][1]
						np_beg = sent2_beg + np_sent[np_beg_tok][3]
						np_end = sent2_beg + np_sent[np_end_tok][4]

						matching_outcomes.append((out1, np, out1_beg, out1_end, np_beg, np_end, np_sent_id))
						out_matched.add(out1)"""


			out_not_matched_final = set(po_list) - out_matched

			for out in (out_not_matched_final):
				out_beg_tok = self.PO_list[po_list.index(out)][2]
				out_end_tok = self.PO_list[po_list.index(out)][3]
				out_sent_id = self.PO_list[po_list.index(out)][4]	
				out_sent = self.sentences_tagged[(out_sent_id, parser)]
				sent_beg = self.sentences[out_sent_id][1]
				out_beg = sent_beg + out_sent[out_beg_tok][3]
				out_end = sent_beg + out_sent[out_end_tok][4]

				outcomes_not_matched.add((out, out_beg, out_end))


			if len(matching_outcomes) != 0:
				col_width = max(len(phrase) for row in matching_outcomes for phrase in [row[0], row[1]]) + 5  # padding
				print("The list of corresponding primary and reported outcomes :")
				meta = meta + "The list of corresponding primary and reported outcomes :\n"
				col_names = "".join(['Primary'.ljust(col_width), 'Reported'.ljust(col_width)])
				print(col_names)
				meta += col_names + "\n"
				for item in matching_outcomes:
					pair = "".join([item[0].ljust(col_width), item[1].ljust(col_width)])
					#print(pair)
					meta += pair + '\n'

			if len(out_not_matched_final) != 0:
				print("There is no corresponding reported outcomes in the abstract for the following primary outcomes: ", out_not_matched_final )
				meta = meta + "There is no corresponding reported outcomes in the abstract for the following primary outcomes:\n"
				for out in out_not_matched_final:
					meta += out + '\n'

			else:
				print("All primary outcomes are reported correctly")
				meta += "All primary outcomes are reported correctly\n"

		
		return matching_outcomes, outcomes_not_matched, meta


	def compare_registry_rep(self, parser = 'bert'):
		meta = ''
		print("Comparing primary outcomes in the registry and reported outcomes in the text of the article")
		matching_outcomes = []
		outcomes_not_matched = set()

		if self.registry_parsed == None:
			self.parse_all_registries()

		if len(self.registry_parsed) == 0:
			print("There is no corresponding registry entry found.")
			meta = "There is no corresponding registry entry found.\n"

		else:
			self.find_out_rep_abstr()
			out_rep_list = [ out[0] for out in self.out_rep_abstr ]

			out_text_matched = set()
			out_reg_matched = set()

			if len(out_rep_list) == 0:
####				print("There are no reported outcomes in the text.")
				meta = "There are no reported outcomes in the text.\n"
			
			else:
				outcome_reg = re.compile("primary\s(outcome|end[ -]?point)", re.IGNORECASE)
				time_reg = re.compile("time", re.IGNORECASE)

				registry_outcomes = set()				

				for item in self.registry_parsed:
					parse_results = eval(item[2])
					for key in parse_results.keys():
						if outcome_reg.search(key):
							if not time_reg.search(key):
								value = [ item for item in parse_results[key] if (item != '' and not re.match('\[Time Frame: .*?\]', item) ) ]
								registry_outcomes = registry_outcomes | set(value)

				if len(registry_outcomes) == 0:
					print("No primary outcomes found in the registry entry.")
					meta = "No primary outcomes found in the registry entry.\n"
				else:
					#comparison = self.compare_outcomes_with_variants(registry_outcomes, out_rep_list)
					comparison = self.compare_outcomes_bert(registry_outcomes, out_rep_list)
			
					for key in comparison.keys():
						if comparison[key]:
							out1 = key[0]
							out2 = key[1]

							out2_beg_tok = self.out_rep_abstr[out_rep_list.index(out2)][2]
							out2_end_tok = self.out_rep_abstr[out_rep_list.index(out2)][3]
							out2_sent_id = self.out_rep_abstr[out_rep_list.index(out2)][4]	
							out2_sent = self.sentences_tagged[(out2_sent_id, parser)]
							sent2_beg = self.sentences[out2_sent_id][1]
							out2_beg = sent2_beg + out2_sent[out2_beg_tok][3]
							out2_end = sent2_beg + out2_sent[out2_end_tok][4]

							matching_outcomes.append((out1, out2, out2_beg, out2_end, out2_sent_id))
							out_reg_matched.add(out1)
							out_text_matched.add(out2)

					out_not_matched_reg = set(registry_outcomes) - out_reg_matched

					if len(matching_outcomes) != 0:
						col_width = max(len(phrase) for row in matching_outcomes for phrase in [row[0], row[1]]) + 5  # padding			
						print("The list of corresponding outcomes from the registry and the text:")
						meta += "The list of corresponding outcomes from the registry and the text:\n"
						col_names = "".join(['Registry'.ljust(col_width), 'Text'.ljust(col_width)])
						#print(col_names)
						meta += col_names + "\n"
						for item in matching_outcomes:
							pair = "".join([item[0].ljust(col_width), item[1].ljust(col_width)])
							#print(pair)
							meta += pair + '\n'

					if len(out_not_matched_reg) != 0:
						print("There is no corresponding reported outcomes in the text for the following outcomes from the registry: ", out_not_matched_reg )
						meta = meta + "There is no corresponding reported outcomes in the text for the following outcomes from the registry:\n"
						for out in out_not_matched_reg:
							meta += out + '\n'

					else:
						print("All primary outcomes from the registry are reported in the text.")
						meta = meta + "All primary outcomes from the registry are reported in the text.\n"

		return matching_outcomes, meta

	def check_outcomes_prominence(self, outcomes_list, parser = 'bert'):
		concessive = {}
		first = {}

		matching_out_positions = []
		for out_pair in outcomes_list:
			out2_sent = self.sentences[out_pair[-1]][0]
			#print(out2_sent)
			out2_beg = out_pair[-3]
			out2_end = out_pair[-2]
			matching_out_positions.append((out2_beg, out2_end))
			if re.search('\\b(but|though|although|spite|despite|however)\\b', out2_sent, re.IGNORECASE):
				concessive[(out2_beg, out2_end)] = True
			#else:
			#	concessive[(out2_beg, out2_end)] = False

		for out_pair in outcomes_list:
			out2_sent = out_pair[-1]
			out2_beg = out_pair[-3]
			out2_end = out_pair[-2]
			for out_rep in self.out_rep_abstr:
				out_rep_beg_tok = self.out_rep_abstr[self.out_rep_abstr.index(out_rep)][2]
				out_rep_end_tok = self.out_rep_abstr[self.out_rep_abstr.index(out_rep)][3]
				out_rep_sent_id = self.out_rep_abstr[self.out_rep_abstr.index(out_rep)][4]	
				out_rep_sent = self.sentences_tagged[(out_rep_sent_id, parser)]
				out_rep_sent_beg = self.sentences[out_rep_sent_id][1]
				out_rep_beg = out_rep_sent_beg + out_rep_sent[out_rep_beg_tok][3]
				out_rep_end = out_rep_sent_beg + out_rep_sent[out_rep_end_tok][4]
				if (out_rep_beg, out_rep_end) not in matching_out_positions:
					if out_rep_beg < out2_beg:
						first[(out2_beg, out2_end)] = False

			#if (out2_beg, out2_end) not in first.keys():
			#	first[(out2_beg, out2_end)] = True

		return concessive, first


	def find_out_signif_rel_bert(self, parser_stat = 'spacy', parser_out = 'bert'):
		if self.outcomes_reported == None:
			#self.preannot_outcomes_bert()
			self.preannot_rep_scibert()

		if self.stats == None:
			self.preannot_stat()

		self.stats = simple_filter_preannot_results(self.stats)

		out_sig_rels = []

		bert_input = []
		# make input data for bert
		for stat in self.stats:
			if stat[4] == 'Type="Pval"':
				stat_beg = stat[1]
				stat_end = stat[2]
				stat_sent = stat[3]

				for out in self.outcomes_reported:
					out_beg = out[1]
					out_end = out[2]
					out_sent = out[3]
					if stat_sent == out_sent:
						sent_text = self.sentences[stat_sent][0]
						sent_beg = self.sentences[stat_sent][1]
						sent_end = self.sentences[stat_sent][2]

						stat_beg_char = self.sentences_tagged[(stat_sent, parser_stat)][stat_beg][3]
						stat_end_char = self.sentences_tagged[(stat_sent, parser_stat)][stat_end][4]
						stat_text = sent_text[stat_beg_char:stat_end_char + 1]

						out_beg_char = self.sentences_tagged[(out_sent, parser_out)][out_beg][3]
						out_end_char = self.sentences_tagged[(out_sent, parser_out)][out_end][4]
						out_text = sent_text[out_beg_char:out_end_char + 1]

						out_beg_text = sent_beg + out_beg_char
						out_end_text = sent_beg + out_end_char

						stat_beg_text = sent_beg + stat_beg_char
						stat_end_text = sent_beg + stat_end_char

						if stat_end_char < out_beg_char:
							sent_mask = sent_text[:stat_beg_char] + "@SIGNIFICANCE" + sent_text[stat_end_char + 1:out_beg_char] + "@OUTCOME" + sent_text[out_end_char + 1:]
						elif out_end_char < stat_beg_char:
							sent_mask = sent_text[:out_beg_char] + "@SIGNIFICANCE" + sent_text[out_end_char + 1:stat_beg_char] + "@OUTCOME" + sent_text[stat_end_char + 1:]
						else:
							print('ERROR intersecting entities')

						print(sent_mask)
						bert_input.append((sent_mask, out_text, stat_text, out_beg_text, out_end_text, stat_beg_text, stat_end_text))

		if len(bert_input) == 0: print('ERROR empty input for BERT')
		results = run_re.main(bert_input)
		for (i, probabilities) in enumerate(results):
			print(probabilities[0], probabilities[1])
			if probabilities[1] > 0.5:
				out_sig_rels.append(bert_input[i][1:])

		os.remove("tmp/predict.tf_record")

		return out_sig_rels


	def generate_report(self, parser = 'spacy'):
		report = "Report of DeSpin\n\n"
		report += "Article's abstract:\n"

		if self.abstract == None:
			self.find_abstract()

		if self.abstract != '':
			report += self.abstract[0]
		else:
			report+= 'Abstract not found.\n'

		report += '=================================\n'
		report += "Checking consistency of primary outcomes in the trial registry and in the text.\n" 
		report += self.compare_po_text_registry()[2]
		report += '=================================\n'
		report += "Checking consistency of primary outcomes in the abstract and in the body.\n" 
		report += self.compare_po_abstr_bt()[2]
		report += '=================================\n'
		report += "Checking if the primary outcomes defined in the text are reported in the results and conclusions of the abstract.\n"
		matching_outcomes, not_matched, meta = self.compare_po_rep()
		concessive, first = self.check_outcomes_prominence(matching_outcomes)
		report += meta
		if len(concessive.keys()) > 0 or len(first.keys()) > 0:
			report += "It is possible that the abstract is focused on non-primary outcomes, please check reporting for the following primary outcomes:\n"
			out_not_focus = [self.text[key[0]:key[1] + 1] for key in concessive.keys()]
			out_not_focus += [self.text[key[0]:key[1] + 1] for key in first.keys()]
			out_not_focus = set(out_not_focus)
			for out in out_not_focus:
				report += out + '\n'			

		report += '=================================\n'		
		report += "Checking if the primary outcomes from the registry are reported in the results and conclusions of the abstract.\n" 
		matching_outcomes, meta = self.compare_registry_rep()
		concessive, first = self.check_outcomes_prominence(matching_outcomes)
		report += meta
		if len(concessive.keys()) > 0 or len(first.keys()) > 0:
			report += "It is possible that the abstract is focused on non-primary outcomes, please check reporting for the following primary outcomes:\n"
			out_not_focus = [self.text[key[0]:key[1] + 1] for key in concessive.keys()]
			out_not_focus += [self.text[key[0]:key[1] + 1] for key in first.keys()]
			out_not_focus = set(out_not_focus)
			for out in out_not_focus:
				report += out + '\n'

		out_sig_rels = self.find_out_signif_rel()

		if len(out_sig_rels) > 0:
			col_width = max(len(phrase) for row in out_sig_rels for phrase in [row[0], row[1]]) + 5  # padding
			report += '=================================\n'
			report += "Outcomes and their significance levels:\n"
			col_names = "".join(['Outcome'.ljust(col_width), 'Significance level'.ljust(col_width)])
			report += col_names + "\n"
			for item in out_sig_rels:
				pair = "".join([item[0].ljust(col_width), item[1].ljust(col_width)])
				report += pair + '\n'

		sim = self.find_sim_synt()
		if len(sim) > 0:
			report += '=================================\n'
			report += "Possible statements of similarity of treatments in Results and Conclusions of the abstract:\n"
			for item in sim:
				sent_id = item[3]
				sent = self.sentences[sent_id][0]
				report += sent + '\n'

		wgc = self.find_wgc_synt()
		if len(wgc) > 0:
			report += '=================================\n'
			report += "Possible within-group comparisons in Results and Conclusions of the abstract:\n"
			for item in wgc:
				sent_id = item[3]
				sent = self.sentences[sent_id][0]
				report += sent + '\n'

		return report


def simple_filter_preannot_results(preannot_results):
	results_len = []	
	for item in preannot_results:
		ent = item[0]
		beg = item[1]
		end = item[2]
		sent_id = item[3] 
		typ = item[4]
		conf = item[5]
		l = end - beg
		results_len.append((ent, beg, end, sent_id, typ, conf, l))

	results_len = list(set(results_len))

	# simple filtering
	res_new = []
	while len(results_len) > 0:
		results_len.sort(key = operator.itemgetter(5))
		item = results_len[0]
		ent = item[0]
		beg = item[1]
		end = item[2]
		sent_id = item[3] 
		typ = item[4]
		conf = item[5]
		list_check = results_len[1:]
		check = 0

		for item_check in list_check:
			ent_check = item_check[0]
			beg_check = item_check[1]
			end_check = item_check[2]
			sent_id_check = item_check[3]
			typ_check = item_check[4]
			conf_check = item_check[5]
			l_check = item_check[6]

			if sent_id == sent_id_check and typ == typ_check:
				if beg >= beg_check and end <= end_check:
					check = 1
					break
											
				elif beg <= beg_check and end >= end_check:
					results_len.remove(item_check)

				elif beg > beg_check and beg <= end_check and end > end_check:
					check = 1
					results_len.remove(item_check)
					results_len.append((ent_check, beg_check, end, sent_id, typ_check, -1, end - beg_check))

				elif beg < beg_check and end >= beg_check and end < end_check:
					check = 1
					results_len.remove(item_check)
					results_len.append((ent, beg, end_check, sent_id, typ, -1, end_check - beg))

		if check == 0:
			res_new.append(item)
			#print(item)
		results_len.pop(0)

	res_new = list(set(res_new))
	return res_new


def advanced_filter_preannot_results(preannot_results):
	results_len = []	
	for item in preannot_results:
		ent = item[0]
		beg = item[1]
		end = item[2]
		sent_id = item[3] 
		typ = item[4]
		conf = item[5]
		l = end - beg
		results_len.append((ent, beg, end, sent_id, typ, conf, l))

	results_len = list(set(results_len))

	# advanced filtering
	res_new = []
	while len(results_len) > 0:
		results_len.sort(key = operator.itemgetter(5))
		item = results_len[0]
		ent = item[0]
		beg = item[1]
		end = item[2]
		sent_id = item[3]
		typ = item[4]
		conf = item[5]
		l = item[6]

		list_check = results_len[1:]
		check = 0

		for item_check in list_check:
			ent_check = item_check[0]
			beg_check = item_check[1]
			end_check = item_check[2]
			sent_id_check = item_check[3]
			typ_check = item_check[4]
			conf_check = item_check[5]
			l_check = item_check[6]

			if sent_id == sent_id_check and beg == beg_check and end == end_check:
				if ent == ent_check:
					if typ == '' and typ_check != '':
						check = 1
						break
					elif typ != '' and typ_check == '':
						results_len.remove(item_check)
					elif typ == '' and typ_check == '':
						check = 1
						break
					elif ent == 'Out' and typ != '' and typ_check != '' and typ != typ_check:
						if typ.find('Type="None"') != -1 and typ_check.find('Type="None"') == -1:
							check = 1
							break
						elif typ_check.find('Type="None"') != -1 and typ.find('Type="None"') == -1:
							results_len.remove(item_check)
						elif typ.find('Type="Prim"') != -1 and typ_check.find('Type="Sec"') != -1:
							check = 1
							break
						elif typ_check.find('Type="Prim"') != -1 and typ.find('Type="Sec"') != -1:
							results_len.remove(item_check)

				else:
					if ent == 'Obj' and (ent_check == 'Subj' or ent_check == 'Out'):
						check = 1
						break
					elif (ent == 'Subj' or ent == 'Out') and ent_check == 'Obj':
						results_len.remove(item_check)

					elif (ent == 'Out' or ent == 'OutTP' or ent == 'Int' or ent == 'Subj') and (ent_check == 'Out' or ent_check == 'OutTP' or ent_check == 'Int' or ent_check == 'Subj'):
						if conf > 0 and conf < conf_check:
							results_len.remove(item_check)

						elif conf > conf_check and conf_check > 0:
							check = 1
							break

			elif sent_id == sent_id_check and beg >= beg_check and end <= end_check:
				if (ent == ent_check and ent == 'Out') and (typ != '' and typ_check != '' and typ != typ_check):
					if typ.find('Type="None"') != -1 and typ_check.find('Type="None"') == -1:
						check = 1
						break
					elif typ_check.find('Type="None"') != -1 and typ.find('Type="None"') == -1:
						results_len.remove(item_check)
					elif typ.find('Type="Prim"') != -1 and typ_check.find('Type="Sec"') != -1:
						check = 1
						break
					elif typ_check.find('Type="Prim"') != -1 and typ.find('Type="Sec"') != -1:
						results_len.remove(item_check)

				elif (ent == ent_check and ent == 'Out' and typ == typ_check and typ.find('Status="Reported"') == -1):
					results_len.remove(item_check)

				elif ent == ent_check and conf != -1:
					check = 1
					break

				elif ent == ent_check and conf == -1:
					results_len.remove(item_check)

					
				elif (ent == 'OutTP' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'OutTP') or (ent == 'Out' and ent_check == 'OutTP') or (ent == 'OutMeas' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'OutMeas') or (ent == 'Aim' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'Aim'):
					continue

				else:
					if (ent == 'Out' or ent == 'OutTP' or ent == 'Int' or ent == 'Subj') and (ent_check == 'Out' or ent_check == 'OutTP' or ent_check == 'Int' or ent_check == 'Subj'):
						if conf > 0 and conf < conf_check:
							results_len.remove(item_check)

						elif conf > conf_check and conf_check > 0:
							check = 1
							break
											

			elif sent_id == sent_id_check and beg <= beg_check and end >= end_check:
				if (ent == ent_check and ent == 'Out') and (typ != '' and typ_check != '' and typ != typ_check):
					if typ.find('Type="None"') != -1 and typ_check.find('Type="None"') == -1:
						check = 1
						break
					elif typ_check.find('Type="None"') != -1 and typ.find('Type="None"') == -1:
						results_len.remove(item_check)
					elif typ.find('Type="Prim"') != -1 and typ_check.find('Type="Sec"') != -1:
						check = 1
						break
					elif typ_check.find('Type="Prim"') != -1 and typ.find('Type="Sec"') != -1:
						results_len.remove(item_check)

				elif (ent == ent_check and ent == 'Out' and typ == typ_check and typ.find('Status="Reported"') == -1):
					check = 1
					break

				elif ent == ent_check and conf_check != -1:
					results_len.remove(item_check)

				elif ent == ent_check and conf_check == -1:
					check = 1
					break

				elif (ent == 'OutTP' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'OutTP') or (ent == 'OutMeas' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'OutMeas') or (ent == 'Aim' and ent_check == 'Out') or (ent == 'Out' and ent_check == 'Aim'):
					continue
		
				else:
					if (ent == 'Out' or ent == 'OutTP' or ent == 'Int' or ent == 'Subj') and (ent_check == 'Out' or ent_check == 'OutTP' or ent_check == 'Int' or ent_check == 'Subj'):
						if conf > 0 and conf < conf_check:
							results_len.remove(item_check)

						elif conf > conf_check and conf_check > 0:
							check = 1
							break

			elif sent_id == sent_id_check and beg > beg_check and beg <= end_check and end > end_check:
				if (ent == ent_check and ent == 'Out') and (typ != '' and typ_check != '' and typ != typ_check):
					if typ.find('Type="None"') != -1 and typ_check.find('Type="None"') == -1:
						check = 1
						break
					elif typ_check.find('Type="None"') != -1 and typ.find('Type="None"') == -1:
						results_len.remove(item_check)
					elif typ.find('Type="Prim"') != -1 and typ_check.find('Type="Sec"') != -1:
						check = 1
						break
					elif typ_check.find('Type="Prim"') != -1 and typ.find('Type="Sec"') != -1:
						results_len.remove(item_check)

				elif ent == 'StatMeas' and ent_check == 'StatMeas':
					results_len.remove(item_check)
					results_len.append((ent_check, beg_check, beg - 1, sent_id, typ_check, -1, beg - 1 - beg_check))


				elif ent == ent_check:
					check = 1
					results_len.remove(item_check)
					results_len.append((ent_check, beg_check, end, sent_id, typ_check, -1, end - beg_check))


				elif ent == 'Subj' and (ent_check == 'Out' or ent_check == 'Aim'):
					results_len.remove(item_check)
					results_len.append((ent_check, beg_check, end, sent_id, typ_check, -1, end - beg_check))


				elif ent == 'OutTP' and ent_check == 'Out':
					results_len.remove(item_check)
					#res_new.append((ent_check, beg_check, beg - 1, typ_check, conf_check, l_check))
					results_len.append((ent_check, beg_check, beg - 1, sent_id, typ_check, -1, beg - 1 - beg_check))

						
				elif ent == 'Out' and ent_check == 'OutTP':
					check = 1
					#res_new.append((ent, end_check + 1, end, typ_check, conf_check, l_check))
					results_len.append((ent, end_check + 1, end, sent_id, typ_check, -1, end - end_check - 1))
					break


				elif (ent == 'Out' or ent == 'OutTP' or ent == 'Int' or ent == 'Subj') and (ent_check == 'Out' or ent_check == 'OutTP' or ent_check == 'Int' or ent_check == 'Subj'):
					if conf > 0 and conf < conf_check:
						results_len.remove(item_check)

					elif conf > conf_check and conf_check > 0:
						check = 1
						break

				else:
					results_len.remove(item_check)
					#res_new.append((ent_check, beg_check, end, typ_check, conf_check, l_check))
					results_len.append((ent_check, beg_check, end, sent_id, typ_check, -1, end - beg_check))



			elif sent_id == sent_id_check and beg < beg_check and end >= beg_check and end < end_check:
				if (ent == ent_check and ent == 'Out') and (typ != '' and typ_check != ''):
					if typ.find('Type="None"') != -1 and typ_check.find('Type="None"') == -1:
						check = 1
						break
					elif typ_check.find('Type="None"') != -1 and typ.find('Type="None"') == -1:
						results_len.remove(item_check)
					elif typ.find('Type="Prim"') != -1 and typ_check.find('Type="Sec"') != -1:
						check = 1
						break
					elif typ_check.find('Type="Prim"') != -1 and typ.find('Type="Sec"') != -1:
						results_len.remove(item_check)

				elif ent == 'StatMeas' and ent_check == 'StatMeas':
					check = 1
					results_len.append((ent, beg, beg_check - 1, sent_id, typ_check, -1, beg_check - 1 - beg))

				elif ent == ent_check:
					check = 1
					results_len.remove(item_check)
					results_len.append((ent, beg, end_check, sent_id, typ, -1, end_check - beg))


				elif ent_check == 'Subj' and (ent == 'Out' or ent == 'Aim'):
					check = 1
					results_len.append((ent, beg, end_check, sent_id, typ, -1, end_check - beg))


				elif ent == 'OutTP' and ent_check == 'Out':
					results_len.remove(item_check)
					#res_new.append((ent_check, end + 1, end_check, typ_check, conf_check, l_check))
					results_len.append((ent_check, end + 1, end_check, sent_id, typ_check, -1, end_check - end - 1))

						
				elif ent == 'Out' and ent_check == 'OutTP':
					check = 1
					#res_new.append((ent, beg, beg_check - 1, typ_check, conf_check, l_check))
					results_len.append((ent, beg, beg_check - 1, sent_id, typ_check, -1, beg_check - 1 - beg))
					break

				elif conf > 0 and conf < conf_check:
					results_len.remove(item_check)

				elif conf > conf_check and conf_check > 0:
					check = 1
					break

				else:
					check = 1
					#res_new.append((ent, beg, end_check, typ, conf, l))
					results_len.append((ent, beg, end_check, sent_id, typ, -1, end_check - beg))

					break

		if check == 0:
			res_new.append(item)
			#print(item)
		results_len.pop(0)

	return res_new
