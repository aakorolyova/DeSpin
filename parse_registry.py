# coding: utf-8
import codecs
import os
import re


def parse_who(text):
	elements_list = ["Prospective Registration", "Primary sponsor", "Target sample size", "Study type", "Study design", "Phase"]

	elem_values = {}
	value_reg = re.compile("<span id=.*?>(.*?)</span>", re.DOTALL)
	
	for element in elements_list:
		pattern = re.compile("<tr>[\s\r\n]*<td style=\"[^\"]*?\">[\s\r\n]*" + element + "\S*[\s\r\n]*</td>[\s\r\n]*<td[^\n]*>[\s\r\n]*(<span id=\S*?>.*?</span>\S*?[\s\r\n]*)+</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(0)
			values = []
			for value_match in value_reg.finditer(elem_match):
				value = value_match.group(1)
				values.append(value)
			elem_values[element] = values


	elements_list2 = ["Countries of recruitment", "Intervention", "Key inclusion &amp; exclusion criteria", "Health Condition", "Primary Outcome", "Secondary Outcome", "Source\(s\) of Monetary Support", "Secondary Sponsor"]

	for element in elements_list2:
		pattern = re.compile("<span>" + element + "\S*</span>[\s\r\n]*</b></font></td>[\s\r\n]*</tr>(<tr>[\s\r\n]*<td valign=\S*><font face=\S* color=\S* size=\S*>[\s\r\n]*(<span id=\S*?>.*?</span>\S*?[\s\r\n]*)+[\s\r\n]*</font></td>.*?</tr>)+", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(0)
			values = []
			for value_match in value_reg.finditer(elem_match):
				value = value_match.group(1)
				values.append(value)
			elem_values[element] = values


	patient_info = ["Age minimum", "Age maximum", "Gender"]
	for element in patient_info:
		pattern = re.compile(element + ":" + "[\s\r\n]*<span id=\S*?>(.*?)</span>", re.IGNORECASE)
		elem_search = pattern.search(text)
		values = []
		if elem_search:
			value = elem_search.group(1)
			values.append(value)
		elem_values[element] = values

	return elem_values

                                    

def parse_nct(text):
	elem_values = {}
	sponsor_reg = re.compile("<div class=\"info-title\">Sponsor:</div>[\s\r\n]*<div class=\"info-text\" id=\"sponsor\">(.*?)</div>", re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]

	purpose_reg = re.compile("<!-- purpose_section -->[\s\r\n]*<div class=\"\S*?\" style=\"\S*?\">[\s\r\n]*<img src=\"\S*\" alt=\"\"/><span class=\"\S*\">&nbsp; Purpose</span>[\s\r\n]*<div class=\"\S*\" style=\"\S*\">[\s\r\n]*<div class=\"\S*\">(.*?)</div><br/>", re.DOTALL | re.IGNORECASE)
	purpose_match = purpose_reg.search(text)
	if purpose_match:
		purpose = purpose_match.group(1)
		elem_values["Purpose"] = [purpose]

	table_reg = re.compile("<!-- condition, intervention, phase summary table -->[\s\r\n]*<div align=\"center\">[\s\r\n]*<table class=\"data_table\" cellspacing=\"0\" cellpadding=\"5\" border=\"1\" width=\"80%\">[\s\r\n]*<tr align=\"left\">[\s\r\n]*<th class=\"header3 pale_banner_color\">[\s\r\n]*<a class='study-link' href=\"/ct2/help/conditions_desc\" title=\"Help on Conditions field\" onclick=\"openPopupWindow\('/ct2/help/conditions_desc',false\); return false;\">Condition</a>[\s\r\n]*</th>[\s\r\n]*<th class=\"header3 pale_banner_color\">[\s\r\n]*<a class='study-link' href=\"/ct2/help/interventions_desc\" title=\"Help on Interventions field\" onclick=\"openPopupWindow\('/ct2/help/interventions_desc',false\); return false;\">Intervention</a>[\s\r\n]*</th>[\s\r\n]*<th class=\"header3 pale_banner_color\">[\s\r\n]*<a class='study-link' href=\"/ct2/help/phase_desc\" title=\"Help on Phase field\" onclick=\"openPopupWindow\('/ct2/help/phase_desc',false\); return false;\">Phase</a>[\s\r\n]*</th>[\s\r\n]*</tr>[\s\r\n]*<tr align=\"left\" valign=\"top\">[\s\r\n]*<td class=\"body3\" nowrap>[\s\r\n]*(.*?)<br/>[\s\r\n]*</td>[\s\r\n]*<td class=\"body3\" nowrap>[\s\r\n]*(.*?)[\s\r\n]*</td>[\s\r\n]*<td class=\"body3\" nowrap>[\s\r\n]*(.*?)[\s\r\n]*<br/>[\s\r\n]*</td>[\s\r\n]*</tr>[\s\r\n]*</table>", re.DOTALL | re.IGNORECASE)
	table_match = table_reg.search(text)
	if table_match:
		condition = table_match.group(1)
		intervention = table_match.group(2)
		phase = table_match.group(3)
		elem_values["Condition"] = [condition]
		elem_values["Intervention"] = [intervention]
		elem_values["Phase"] = [phase]


	type_reg = re.compile("<tr valign=\"top\">[\s\r\n]*<td headers=\"studyInfoColTitle\" nowrap>(Study Type|Study Design):</td>[\s\r\n]*<td headers=\"studyInfoColData\" style=\"padding-left:1em\">[\s\r\n]*(.*?)[\s\r\n]*</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	for type_match in type_reg.finditer(text):
		key = type_match.group(1)
		value = type_match.group(2)
		elem_values[key] = [value]


	#outcome_reg = re.compile("<div class=\"body3\">(Primary Outcome Measures|Secondary Outcome Measures):[\s\r\n]*<ul style=\"margin-top:1ex; margin-bottom:1ex;\">[\s\r\n]*<li style=\"margin-top:0.7ex;\">(.*?)<br/>[\s\r\n]*</ul>[\s\r\n]*</div>[\s\r\n]*<br/>", re.DOTALL | re.IGNORECASE)

	outcome_reg = re.compile('<span style="display:inline;" class="term" data-term="(Primary|Secondary) Outcome Measure" title="Show definition">\\1 Outcome Measures <i class="fa fa-info-circle term" aria-hidden="true" data-term="\\1 Outcome Measure"></i></span>[\s\r\n]*:[\s\r\n]*<ol style="margin-top:1ex; margin-bottom:1ex;">[\s\r\n]*<li style="margin-top:0.7ex;">([^<>]+)<br/>[\s\r\n]*</ol>', re.DOTALL | re.IGNORECASE)
	for outcome_match in outcome_reg.finditer(text):
		key = outcome_match.group(1) + ' outcome measure'
		value = outcome_match.group(2)
		elem_values[key] = [value]
  
	inclusion_reg = re.compile("Inclusion Criteria:</p>[\s\r\n]*<ul style=[^<>]*?>[\s\r\n]*<li style=\S+>(.*?)</li>[\s\r\n]*</ul>", re.DOTALL | re.IGNORECASE)
	for inclusion_match in inclusion_reg.finditer(text):
		value = inclusion_match.group(1)
		elem_values["Inclusion Criteria"] = [value]  
      
   
	enroll_reg = re.compile("<td headers=\"enrollmentInfoTitle\" nowrap> Enrollment:</td>[\s\r\n]*<td headers=\"enrollmentInfoData\" style=\"padding-left:1em\">(.*?)</td>")
	enroll_match = enroll_reg.search(text)
	if enroll_match:
		enroll_num = enroll_match.group(1)
		elem_values["Enrollment"] = [enroll_num]

	agesex_reg = re.compile("<td headers=\"elgType\" nowrap>(Ages|Sexes) Eligible for Study: &nbsp; </td>[\s\r\n]*<td headers=\"elgData\" style=\"padding-left:1em\">(.*?)</td>[\s\r\n]*</tr>")
	for agesex_match in agesex_reg.finditer(text):
		key = agesex_match.group(1)
		value = agesex_match.group(2)
		elem_values[key] = [value]

	#TO ADD:
	#Inclusion/exclision criteria
	#Arms + interventions


	return elem_values



def parse_isrctn(text):
	elements_list = ["Study hypothesis", "Study design", "Primary study design", "Secondary study design", "Trial type", "Condition", "Intervention", "Phase", "Drug names", "Primary outcome measures", "Secondary outcome measures", "Participant inclusion criteria", "Participant type", "Age group", "Gender", "Target number of participants", "Participant exclusion criteria", "Countries of recruitment", "Sponsor details", "Funder name", "Participant level data"]
	elem_values = {}
	for element in elements_list:
		pattern = re.compile("<h3 class=\"Info_section_title \S*?\">" + element + "</h3>[\s\r\n]*<p class=\".*?\">[\s\r\n]*?(.*?)[\s\r\n]*?</p>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(1)
			elem_values[element] = [elem_match]
	return elem_values


def parse_ntr(text):
	elements_list = ["hypothesis", "Healt Condition\(s\) or Problem\(s\) studied", "Inclusion criteria", "Exclusion criteria", "randomised", "Type", "Studytype", "Target number of participants", "Interventions", "Primary outcome", "Secondary outcome", "Timepoints", "Sponsor/Initiator", "Funding<br>\n\(Source\(s\) of Monetary or Material Support\)", "Brief summary"]
	elem_values = {}
	for element in elements_list:
		pattern = re.compile("- " + element + "</td><td class='rightcol'>(.*?)</td><tr><tr class='\S*?'><td class='leftcol'>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(1)
			elem_values[element] = [elem_match]
	return elem_values



def parse_slctr(text):
	elements_list = ["Disease of Health Condition\(s\) Studied", "What is the research question being addressed\?", "Type of study", "Allocation", "Control", "Purpose", "Intervention\(s\) planned", "Inclusion criteria", "Exclusion criteria", "Primary outcome\(s\)", "Primary outcome\(s\) - Time of assessment\(s\)", "Secondary outcome", "Secondary outcome\(s\) - Time of assessment\(s\)", "Target number/sample size", "Countries of recruitment", "Funding source"]
	elem_values = {}
	for element in elements_list:
		pattern = re.compile("<div class=\"row\">[\s\r\n]*<div class=\"\S*?\">[\s\r\n]*<p class=\"light\">" + element + "</p>[\s\r\n]*</div>[\s\r\n]*<div class=\"\S*?\">[\s\r\n]*(?:<div>)?<p>(.*?)</p>[\s\r\n]*?(?:</div>)?[\s\r\n]*?</div>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(1)
			elem_values[element] = [elem_match]

	sponsor_reg = re.compile("<p class=\"light\">Primary study sponsor/organization</p>[\s\r\n]*<p><span>(.*?)</span>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]

	return elem_values


def parse_ctri(text):
	elem_values = {}
	type_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>(Type of Trial|Study Design|Phase of Trial|Brief Summary).*?&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	for type_match in type_reg.finditer(text):
		key = type_match.group(1)
		value = type_match.group(2)
		elem_values[key] = [value]

	sponsor_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>Primary Sponsor</b>.*?&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>[\s\r\n]*<tr>[\s\r\n]*<td><b>Name&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]

	countries_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>Countries of Recruitment</b>.*?&nbsp;</td>[\s\r\n]*<td>&nbsp;(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	countries_match = countries_reg.search(text)
	if countries_match:
		countries = countries_match.group(1)
		elem_values["Countries"] = [countries]

	condition_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>Health Condition / Problems Studied</b>.*?&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>[\s\r\n]*<tr[^<>]*?>[\s\r\n]*<td><font color=\"white\"><b>Health Type&nbsp;</td>[\s\r\n]*<td><font color=\"white\"><b>Condition&nbsp;</td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	condition_match = condition_reg.search(text)
	if condition_match:
		health_type = condition_match.group(1)
		condition = condition_match.group(2)
		elem_values["Health Type"] = [health_type]
		elem_values["Condition"] = [condition]

	treatments_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>Intervention / Comparator Agent</b>.*?&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>[\s\r\n]*<tr[^<>]*?>[\s\r\n]*<td><font color=\"white\"><b>Type&nbsp;</td>[\s\r\n]*<td><font color=\"white\"><b>Name&nbsp;</td>[\s\r\n]*<td><font color=\"white\"><b>Details&nbsp;</td>[\s\r\n]*</tr>[\s\r\n]*(<tr>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*)+</table>", re.DOTALL | re.IGNORECASE)
	treatments_match = treatments_reg.search(text)
	if treatments_match:
		treatments = treatments_match.group(0)
		reg = re.compile("<tr>[\s\r\n]*?<td>(.*?)</td>[\s\r\n]*?<td>(.*?)</td>[\s\r\n]*?<td>(.*?)</td>[\s\r\n]*?</tr>", re.IGNORECASE)
		for match in reg.finditer(treatments):
			typen = match.group(1)
			treatmt = match.group(2)
			detail = match.group(3)
			elem_values[typen] = [treatmt]
			elem_values[typen + " details"] = [detail]


	inclusion_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>Inclusion Criteria</b>.*?&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>[\s\r\n]*<tr>[\s\r\n]*<td>[\s\r\n]*<b>(Age From)</b>&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td><b>(Age To)</b>&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td>[\s\r\n]*<b>(Gender)</b>&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td><b>(Details)</b>&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*</table>", re.DOTALL | re.IGNORECASE)
	inclusion_match = inclusion_reg.search(text)
	if inclusion_match:
		age1 = inclusion_match.group(1)
		age1_val = inclusion_match.group(2)
		age2 = inclusion_match.group(3)
		age2_val = inclusion_match.group(4)
		gender = inclusion_match.group(5)
		gender_val = inclusion_match.group(6)
		details = inclusion_match.group(8)
		elem_values[age1] = [age1_val]
		elem_values[age2] = [age2_val]
		elem_values[gender] = [gender_val]
		elem_values["Inclusion criteria"] = [details]


	exclusion_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>ExclusionCriteria&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>.*?<td><b>Details</b>&nbsp;</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*</table>", re.DOTALL | re.IGNORECASE)
	exclusion_match = exclusion_reg.search(text)
	if exclusion_match:
		details = exclusion_match.group(1)
		elem_values["Exclusion criteria"] = [details]

	outcome_reg = re.compile("<tr>[\s\r\n]*<td>[\s\r\n]*<b>(Primary Outcome|Secondary Outcome)</b>.*?&nbsp;</td>[\s\r\n]*<td>[\s\r\n]*<table[^<>]+?>[\s\r\n]*<tr[^<>]*?>[\s\r\n]*<td><font color=\"white\"><b>Outcome&nbsp;</td>[\s\r\n]*<td><font color=\"white\"><b>TimePoints&nbsp;</td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*</table>", re.DOTALL | re.IGNORECASE)
	for outcome_match in outcome_reg.finditer(text):
		type_out = outcome_match.group(1)
		outcome = outcome_match.group(2)
		timepoint = outcome_match.group(3)
		elem_values[type_out] = [outcome]
		elem_values[type_out + " timepoints"] = [timepoint]


	sample_reg = re.compile("<td><b>Total Sample Size=</b>\"(.*?)\"<br /><b>Sample Size from India=</b>\"(.*?)\"&nbsp;</td>", re.IGNORECASE)
	sample_match = sample_reg.search(text)
	if sample_match:
		elem_values["Total Sample Size"] = [sample_match.group(1)]
		elem_values["Sample Size from India"] = [sample_match.group(2)]

	return elem_values


def parse_drks(text):
	elem_values = {}
	summaries_reg = re.compile("<div class=\"dummy_empty_p\">start of 1:1-Block public summary</div>[\s\r\n]*<h2 class=\"publicSummary\">Brief Summary in Lay Language</h2>[\s\r\n]*<p class=\"publicSummary\">(.*?)<div class=\"dummy_empty_p\">end of 1:1-Block public summary</div>[\s\r\n]*<div class=\"dummy_empty_p\">start of 1:1-Block scientific synopsis</div>[\s\r\n]*<h2 class=\"scientificSynopsis\">Brief Summary in Scientific Language</h2>[\s\r\n]*<p class=\"scientificSynopsis\">(.*?)<div class=\"dummy_empty_p\">end of 1:1-Block scientific synopsis</div>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	summaries_match = summaries_reg.search(text)
	if summaries_match:
		public_summary = summaries_match.group(1)
		scientific_summary = summaries_match.group(2)
		elem_values["Public summary"] = [public_summary]
		elem_values["Scientific summary"] = [scientific_summary]

	paramli_reg = re.compile("<li class=\"(health-condition|intervention|type|typeNotInterventional|allocation|control|purpose|phase|gender|minAge|maxAge|targetSize)\">[\s\r\n]*<label>(.*?)</label>(.*?)</li>", re.DOTALL | re.IGNORECASE)
	for paramli_match in paramli_reg.finditer(text):
		param = paramli_match.group(1)
		label = paramli_match.group(2)
		value = label + '\t' + paramli_match.group(3)
		if param in elem_values.keys():
			elem_values[param].append(value)
		else:
			elem_values[param] = []
			elem_values[param].append(value)

	paramp_reg = re.compile("<p class=\"(primaryEndpoint|secondaryEndpoints|inclusionAdd|exclusion)\">(.*?)</p>", re.DOTALL | re.IGNORECASE)
	for paramp_match in paramp_reg.finditer(text):
		typep = paramp_match.group(1)
		value = paramp_match.group(2)
		if typep in elem_values.keys():
			elem_values[typep].append(value)
		else:
			elem_values[typep] = []
			elem_values[typep].append(value)

	countries_reg = re.compile("<ul class=\"recruitmentCountries\">.*?</ul>", re.DOTALL | re.IGNORECASE)
	countries_match = countries_reg.search(text)
	if countries_match:
		elem_values["Countries"] = []
		countries = countries_match.group(0)
		reg = re.compile("<li class=\"country\">[\s\r\n]*<label>(.*?)</li>", re.DOTALL | re.IGNORECASE)
		for match in reg.finditer(countries):
			country = match.group(1)
			elem_values["Countries"].append(country)

	funding_reg = re.compile("<li class=\"(materialSupport)\">[\s\r\n]*<label>(.*?)</label>", re.DOTALL | re.IGNORECASE)
	for funding_match in funding_reg.finditer(text):
		param = funding_match.group(1)
		value = funding_match.group(2)
		elem_values[param] = []
		elem_values[param].append(value)


	if text.find("This trial has been registered retrospectively") is not -1:
		elem_values["Registration"] = ["Retrospective"]

	return elem_values


def parse_eudract(text):
	elements_list = ["Sponsor Name", "Medical condition", "Disease", "Population Age", "Gender", "Trial protocol"]
	elem_values = {}
	for element in elements_list:
		pattern = re.compile("<span class=\"label\">" + element + ":</span>(.*?)</td>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(1)
			elem_values[element] = [elem_match]
	return elem_values

def parse_eudract_protocol(text):
	elements_list = ["Name of Sponsor", "Trade name", "Medical condition\(s\) being investigated", "Medical condition in easily understood language", "Main objective of the trial", "Secondary objectives of the trial", "Principal inclusion criteria", "Principal exclusion criteria", "Primary end point", "Secondary end point", "Randomised", "Trial has subjects under 18", "In Utero", "Preterm newborn infants", "Newborns", "Infants and toddlers", "Children", "Adolescents", "Adults", "Elderly", "Female ", "Male"]
	elem_values = {}
	for element in elements_list:
		pattern = re.compile("<td class=\S+?>" + element + "[^<>]*?</td>[\s\r\n]*<td class=\S+?>(?:[\s\r\n]*<table[^<>]*?>[\s\r\n]*<tr>[\s\r\n]*<td[^<>]*?>)?(.*?)</td>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem_match = elem_search.group(1)
			elem_values[element] = [elem_match]
	return elem_values    

#RPCEC: current example is not in English

def parse_rbr(text):
	elem_values = {}

	condition_reg = re.compile("<span class=\"label\">Condições de saúde ou problemas:</span></p>.*?<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	condition_match = condition_reg.search(text)
	if condition_match:
		condition = condition_match.group(1)
		elem_values["Condition"] = [condition]

	intervention_reg = re.compile("<span class=\"label\">Intervenções:</span></p>.*?<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	intervention_match = intervention_reg.search(text)
	if intervention_match:
		intervention = intervention_match.group(1)
		elem_values["Intervention"] = [intervention]
			
	population_reg = re.compile("<tr>[\s\r\n]*<th>Tamanho da amostra alvo:</th>[\s\r\n]*<th>Gênero para inclusão:</th>[\s\r\n]*<th>Idade mínima para inclusão:</th>[\s\r\n]*<th>Idade máxima para inclusão:</th>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	population_match = population_reg.search(text)
	if population_match:
		sample_size = population_match.group(1)
		gender = population_match.group(2)
		minage = population_match.group(3)
		maxage = population_match.group(4)
		elem_values["Target sample size"] = [sample_size]
		elem_values["Gender"] = [gender]
		elem_values["Age minimum"] = [minage]
		elem_values["Age maximum"] = [maxage]


	inclusion_reg = re.compile("<span class=\"label\">Critérios de inclusão:</span></p>.*?<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	inclusion_match = inclusion_reg.search(text)
	if inclusion_match:
		inclusion = inclusion_match.group(1)
		elem_values["Inclusion criteria"] = [inclusion]

	exclusion_reg = re.compile("<span class=\"label\">Critérios de exclusão:</span></p>.*?<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	exclusion_match = exclusion_reg.search(text)
	if exclusion_match:
		exclusion = exclusion_match.group(1)
		elem_values["Exclusion criteria"] = [exclusion]

	design_reg = re.compile("<span class=\"label\">Desenho do estudo:</span></p>.*?<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	design_match = design_reg.search(text)
	if design_match:
		design = design_match.group(1)
		elem_values["Design"] = [design]

	outcome_prim_reg = re.compile("<li>[\s\r\n]*<p><span class=\"label\">Desfechos primários:</span></p>.*?</li>", re.DOTALL | re.IGNORECASE)
	outcome_prim_match = outcome_prim_reg.search(text)
	if outcome_prim_match:
		elem_values["Primary outcome"] = []
		outcome_prim = outcome_prim_match.group(0)
		outcomes_reg = re.compile("<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
		for outcome_match in outcomes_reg.finditer(outcome_prim):
			outcome = outcome_match.group(1)
			elem_values["Primary outcome"].append(outcome)

	outcome_sec_reg = re.compile("<li>[\s\r\n]*<p><span class=\"label\">Desfechos secundários:</span></p>.*?</li>", re.DOTALL | re.IGNORECASE)
	outcome_sec_match = outcome_sec_reg.search(text)
	if outcome_sec_match:
		elem_values["Secondary outcome"] = []
		outcome_sec = outcome_sec_match.group(0)
		outcomes_reg = re.compile("<div class=\"title\">[\s\r\n]*<h2>en</h2>[\s\r\n]*<p>(.*?)</p>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
		for outcome_match in outcomes_reg.finditer(outcome_sec):
			outcome = outcome_match.group(1)
			elem_values["Secondary outcome"].append(outcome)

	countries_reg = re.compile("<span class=\"legend\">País de recrutamento</span>.*?</ul>", re.DOTALL | re.IGNORECASE)
	countries_match = countries_reg.search(text)
	if countries_match:
		elem_values["Countries"] = []
		countries = countries_match.group(0)
		country_reg = re.compile("<li>(.*?)</li>")
		for country_match in country_reg.finditer(countries):
			country = country_match.group(1)
			elem_values["Countries"].append(country)

	return elem_values




def parse_actrn(text):
	elem_values = {}

	registration_reg = re.compile("<div class=\"review-element-name\">[\s\r\n]*Type of registration[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"ctl00_body_lblTrialType\">(.*?)</span>[\s\r\n]*</div>", re.DOTALL | re.IGNORECASE)
	registration_match = registration_reg.search(text)
	if registration_match:
		registration = registration_match.group(1)
		elem_values["Registration"] = [registration]


	conditions_reg = re.compile("Health condition\(s\) or problem\(s\) studied:[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*(<div class=\"review-form-block\">[\s\r\n]*<div class=\"review-element-block\">[\s\r\n]*<div class=\"review-element-content health\">[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\">.*?</span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hide\">.*?</span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hide\">.*?</span>[\s\r\n]*<div id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hidden\">[\s\r\n]*<span class=\"query\">Query\! </span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\"></span>[\s\r\n]*[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*)+", re.DOTALL | re.IGNORECASE)
	conditions_match = conditions_reg.search(text)
	if conditions_match:
		elem_values["Condition"] = []
		conditions = conditions_match.group(0)
		condition_reg = re.compile("<div class=\"review-form-block\">[\s\r\n]*<div class=\"review-element-block\">[\s\r\n]*<div class=\"review-element-content health\">[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\">(.*?)</span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hide\">.*?</span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hide\">.*?</span>[\s\r\n]*<div id=\"\S+?TXHEALTHCONDITION\S+?\" class=\"hidden\">[\s\r\n]*<span class=\"query\">Query\! </span>[\s\r\n]*<span id=\"\S+?TXHEALTHCONDITION\S+?\"></span>[\s\r\n]*[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*", re.DOTALL | re.IGNORECASE)
		for condition_match in condition_reg.finditer(conditions):
			condition = condition_match.group(1)
			elem_values["Condition"].append(condition)


	type_reg = re.compile("<span id=\"ctl00_body_lbl_CXSTUDYTYPE\">Study type</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"ctl00_body_CXSTUDYTYPE\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	type_match = type_reg.search(text)
	if type_match:
		type = type_match.group(1)
		elem_values["Type"] = [type]
      
	intervention_reg = re.compile("<span id=\"\S+?CXINTERVENTIONS\">Description of intervention\(s\) / exposure</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CXINTERVENTIONS\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	intervention_match = intervention_reg.search(text)
	if intervention_match:
		intervention = intervention_match.group(1)
		elem_values["Intervention"] = [intervention]

	comparator_reg = re.compile("<span id=\"\S+?CXCOMPARATOR\">Comparator / control treatment</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CXCOMPARATOR\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	comparator_match = comparator_reg.search(text)
	if comparator_match:
		comparator = comparator_match.group(1)
		elem_values["Comparator"] = [comparator]
      
	control_group_reg = re.compile("<span id=\"\S+?CXCONTROL\">Control group</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CXCONTROL\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	control_group_match = control_group_reg.search(text)
	if control_group_match:
		control_group = control_group_match.group(1)
		elem_values["Control group"] = [control_group]

      
	outcome_reg = re.compile("<span id=\"\S+?CXOUTCOME\">((?:Primary|Secondary) outcome \[(\d+)\])</span>[\s\r\n]*<span id=\"\S+?CXOUTCOME_ID\" class=\"hide\">.*?</span>[\s\r\n]*<span id=\"\S+?CXOUTCOME_UPDATEID\" class=\"hide\">.*?</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CXOUTCOME\">(.*?)</span>[\s\r\n]*<div id=\"\S+?CXOUTCOME\" class=\"hidden\">[\s\r\n]*<span class=\"query\">Query\! </span>[\s\r\n]*<span id=\"\S+?CXOUTCOME\"></span>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-form-block\">[\s\r\n]*<div class=\"review-element-block\">[\s\r\n]*<div class=\"review-element-name timepoint\">[\s\r\n]*<span id=\"\S+?CXTIMEPOINT\">Timepoint \[\\2\]</span>[\s\r\n]*<span id=\"\S+?CXTIMEPOINT_ID\" class=\"hide\">.*?</span>[\s\r\n]*<span id=\"\S+?CXTIMEPOINT_UPDATEID\" class=\"hide\">.*?</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CXTIMEPOINT\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	for outcome_match in outcome_reg.finditer(text):
		out_type = outcome_match.group(1)
		outcome = outcome_match.group(3)
		timepoint = outcome_match.group(4)
		elem_values[out_type] = [outcome]
		elem_values[out_type + ' timepoint' ] = [timepoint]



	criteria_reg = re.compile("<span id=\"\S+?CRITERIA\">Key (inclusion criteria|exclusion criteria)</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?CRITERIA\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	for criteria_match in criteria_reg.finditer(text):
		criteria_type = criteria_match.group(1)
		criteria = criteria_match.group(2)
		elem_values[criteria_type] = [criteria]
		

	age_reg = re.compile("<span id=\"\S+?AGE\">(Minimum age|Maximum age)</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?AGE\">(.*?)</span>[\s\r\n]*<span id=\"\S+?AGETYPE\">(.*?)</span>[\s\r\n]*<div id=\"\S+?AGE\" class=\"hidden\">", re.DOTALL | re.IGNORECASE)
	for age_match in age_reg.finditer(text):
		age_type = age_match.group(1)
		age = age_match.group(2) + ' ' + age_match.group(3)
		elem_values[age_type] = [age]
      
  
	gender_reg = re.compile("<span id=\"\S+?GENDER\">Gender</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?GENDER\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	gender_match = gender_reg.search(text)
	if gender_match:
		gender = gender_match.group(1)
		elem_values["Gender"] = [gender]

            
	params_reg = re.compile("<span id=\"\S+?\">(Allocation to intervention|Phase)</span>[\s\r\n]*</div>[\s\r\n]*<div class=\"review-element-content\">[\s\r\n]*<span id=\"\S+?\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	for params_match in params_reg.finditer(text):
		param_type = params_match.group(1)
		param = params_match.group(2)
		elem_values[param_type] = [param]
      
            
	anticip_sample_reg = re.compile("<span id=\"\S+?CXSAMPLESIZE\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	anticip_sample_match = anticip_sample_reg.search(text)
	if anticip_sample_match:
		anticip_sample = anticip_sample_match.group(1)
		elem_values["Anticipated sample size"] = [anticip_sample]


	actual_sample_reg = re.compile("<span id=\"\S+?CXACTUALSAMPLESIZE\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	actual_sample_match = actual_sample_reg.search(text)
	if actual_sample_match:
		actual_sample = actual_sample_match.group(1)
		elem_values["Actual sample size"] = [actual_sample]    
              
	summary_reg = re.compile("<span id=\"\S+?body_CXSUMMARY\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	summary_match = summary_reg.search(text)
	if summary_match:
		summary = summary_match.group(1)
		elem_values["Summary"] = [summary]     
      
	sponsor_reg = re.compile("<span id=\"ctl00_body_CXPRIMARYSPONSORNAME\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]  
      

	return elem_values




def parse_chictr(text):
	elem_values = {}

	elements_list = ["Registration Status", "Primary sponsor", "Target disease", "Study type", "Study phase", "Objectives of Study", "Description for medicine or protocol of treatment in detail", "Study design", "Inclusion criteria", "Exclusion criteria", "Gender"]
	for element in elements_list:
		pattern = re.compile("<p class=\"en\">[\s\r\n]*" + element + "：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*<p class=\"en\">(.*?)</p>[\s\r\n]*</td>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			value = elem_search.group(1)
			elem_values[element] = [value]

	outcome_reg = re.compile("<p class=\"en\">[\s\r\n]*Outcome：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td width=\"\S+?\">[\s\r\n]*<p class=\"en\">[\s\r\n]*(.*?)</p>[\s\r\n]*</td>[\s\r\n]*<td width=\"\S+?\" class=\"\S*?\">[\s\r\n]*<p class=\"en\">[\s\r\n]*Type：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*<p class=\"en\">[\s\r\n]*(.*?)</p>[\s\r\n]*</td>[\s\r\n]*</tr>.*?<p class=\"en\">[\s\r\n]*Measure time point of outcome：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*<p class=\"en\">(.*?)</p>[\s\r\n]*</td>[\s\r\n]*<td class=\"\S*?\">[\s\r\n]*<p class=\"en\">[\s\r\n]*Measure method：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*<p class=\"en\">(.*?)</p>[\s\r\n]*</td>", re.DOTALL | re.IGNORECASE)
	n = 0
	for outcome_match in outcome_reg.finditer(text):
		n = n+1
		outcome = outcome_match.group(1)
		out_type = outcome_match.group(2)
		timepoint = outcome_match.group(3)
		method = outcome_match.group(4)
		elem_values["Outcome " + str(n)] = [outcome]
		elem_values["Outcome type " + str(n)] = [out_type]
		elem_values["Outcome timepoint " + str(n)] = [timepoint]
		elem_values["Outcome measure method " + str(n)] = [method]


	ages_reg = re.compile("<td>[\s\r\n]*<span class=\"cn\">.*?</span>[\s\r\n]*<span class=\"en\">(Min age|Max age)</span>[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*(\d*)[\s\r\n]*</td>[\s\r\n]*<td>[\s\r\n]*<span class=\"cn\">.*?</span> <span class=\"en\">(.*?)</span>", re.DOTALL | re.IGNORECASE)
	for age_match in ages_reg.finditer(text):
		age_type = age_match.group(1)
		age = age_match.group(2) + ' ' + age_match.group(3)
		elem_values[age_type] = [age]                 

	intervention_reg = re.compile("<p class=\"en\">[\s\r\n]*Intervention：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td width=\"\S+?\" class=\"sub\">[\s\r\n]*<p class=\"en\">[\s\r\n]*(.*?)</p>[\s\r\n]*</td>", re.DOTALL | re.IGNORECASE)
	elem_values["Intervention"] = []
	for intervention_match in intervention_reg.finditer(text):
		intervention = intervention_match.group(1)
		elem_values["Intervention"].append(intervention)
                                 
	country_reg = re.compile("Countries of recruitment and research settings：.*?<p class=\"en\">[\s\r\n]*Country：[\s\r\n]*</p>[\s\r\n]*</td>[\s\r\n]*<td width=\"\S+?\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	country_match = country_reg.search(text)
	if country_match:
		country = country_match.group(1)
		elem_values["Country"] = [country]
  
	return elem_values


def parse_kct(text):
	elem_values = {}

	sponsor_reg = re.compile("<th scope=\"col\" colspan=\"\S+?\" class=\"tbtit\">Sponsor Organization 1&nbsp;</th>[\s\r\n]*</tr>[\s\r\n]*<tr class=\"tb_clset\">[\s\r\n]*<th scope=\"row\">- Organization Name</th>[\s\r\n]*<td class=\"kline\" colspan=\"\S+?\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]  

	elements_list = ["Target Sample Size", "Lay Summary", "Study Type", "Phase", "Allocation", "Intervention Description", "Condition\(s\)/Problem\(s\)", "Exclusion Criteria", "Gender", "Age", "Description", "Type of Primary Outcome"]
	for element in elements_list:
		pattern = re.compile("<th scope=\"row\".*?>" + element + "[\s\r\n]*</th>[\s\r\n]*<td class=.*?>(.*?)</td>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			value = elem_search.group(1)
			elem_values[element] = [value]

	outcomes_reg = re.compile("<tr>[\s\r\n]+<th scope=\"col\" colspan=\"3\" class=\"tbtit\">((?:Primary|Secondary) Outcome\(s\) \d+)&nbsp;</th>[\s\r\n]*</tr>[\s\r\n]*<tr class=\"tb_clset\">[\s\r\n]*<th scope=\"row\">- Outcome</th>[\s\r\n]*<td class=\"kline\" colspan=\"2\">(.*?)</td>[\s\r\n]*</tr>[\s\r\n]*<tr class=\"tb_clset\">[\s\r\n]*<th scope=\"row\">- Timepoint</th>[\s\r\n]*<td class=\"kline\" colspan=\"2\">(.*?)</td>[\s\r\n]*</tr>", re.DOTALL | re.IGNORECASE)
	for outcome_match in outcomes_reg.finditer(text):
		out_type = outcome_match.group(1)
		outcome = outcome_match.group(2)
		timepoint = outcome_match.group(3)
		elem_values[out_type] = [outcome]
		elem_values[out_type + " timepoint"] = [timepoint]


	return elem_values


def parse_umin(text):
	elem_values = {}

	region_reg = re.compile("<td.*?>Region</font></b></td>[\s\r\n]*<td.*?>[\s\r\n]*<tr>[\s\r\n]*<td.*?\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	region_match = region_reg.search(text)
	if region_match:
		region = region_match.group(1)
		elem_values["Region"] = [region]


	elements_list = ["Condition", "objectives", "Developmental phase", "Primary outcomes", "Key secondary outcomes", "Study type", "Randomization", "Control", "Interventions/Control", "Gender", "Key inclusion criteria", "Key exclusion criteria", "Target sample size"]
	for element in elements_list:
		pattern = re.compile("<td .*?>([^<>]*?" + element + "[^<>]*?)</font></b></td>[\s\r\n]*<td.*?>(.*?)</td>", re.DOTALL | re.IGNORECASE)
		for elem_search in pattern.finditer(text):
			elem = elem_search.group(1)
			value = elem_search.group(2)
			elem_values[elem] = [value]


	age_reg = re.compile("<td.*?>(Age-lower limit|Age-upper limit)</font></b></td>[\s\r\n]*<td.*?>[\s\r\n]*<tr>[\s\r\n]*<td>(.*?)</td>[\s\r\n]*<td>(.*?)</td>", re.DOTALL | re.IGNORECASE)
	for age_match in age_reg.finditer(text):
		age_type = age_match.group(1)
		age = age_match.group(2)
		elem_values[age_type] = [age]


	sponsor_reg = re.compile("<td.*?>Sponsor</font></b></td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td.*?>.*?</font></b></td>[\s\r\n]*<td.*?>(.*?)</td>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]  

	return elem_values


def parse_pactr(text):
	elem_values = {}

	elements_list = ["Brief summary", "Type of trial", "Disease", "Anticipated target sample size", "Actual target sample size"]
	for element in elements_list:
		pattern = re.compile("<td.*?><span class=.*?><strong>(" + element + ".*?)</strong></span>.*?</td>[\s\r\n]*<td=.*?>(?:<span.*?>)?(.*?)(?:</span.*?>)?</td>", re.DOTALL | re.IGNORECASE)
		elem_search = pattern.search(text)
		if elem_search:
			elem = elem_search.group(1)
			value = elem_search.group(2)
			elem_values[elem] = [value]

	allocation_reg = re.compile("<td.*?><span.*?><strong>Allocation to intervention</strong></span></td>[\s\r\n]*(?:<td width=\S+ align=\"center\" valign=\"top\"><span class=\"style26\"><strong>.*?</strong></span></td>[\s\r\n]*)+</tr>[\s\r\n]*<tr>[\s\r\n]*<td.*?align=\"left\" valign=\"top\" class=\"style29\">.*?</td>[\s\r\n]*<td align=\"left\" valign=\"top\" class=\"style29\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	allocation_match = allocation_reg.search(text)
	if allocation_match:
		allocation = allocation_match.group(1)
		elem_values["Allocation"] = [allocation]

	outcome_reg = re.compile("<td align=\"left\" valign=\"top\" class=\"style29\">(Primary Outcome|Secondary Outcome)</td>[\s\r\n]*<td align=\"left\" valign=\"top\" class=\"style29\">(.*?)</td>[\s\r\n]*<td align=\"left\" valign=\"top\" class=\"style29\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	n=0
	for outcome_match in outcome_reg.finditer(text):
		n = n + 1
		out_type = outcome_match.group(1) + ' ' + str(n)
		outcome = outcome_match.group(2)
		timepoint = outcome_match.group(3)
		elem_values[out_type] = [outcome]
		elem_values[out_type + " timepoint"] = [timepoint]


	sponsor_reg = re.compile("Primary Sponsor</td>[\s\r\n]*<td align=\"left\" valign=\"top\" class=\"style29\">(.*?)</td>", re.DOTALL | re.IGNORECASE)
	sponsor_match = sponsor_reg.search(text)
	if sponsor_match:
		sponsor = sponsor_match.group(1)
		elem_values["Sponsor"] = [sponsor]


	population_reg = re.compile("<td.*?><span class=\"style26\"><strong>List (inclusion criteria)</strong></span></td>[\s\r\n]*<td.*?><span class=\"style26\"><strong>List (exclusion criteria)</strong></span></td>[\s\r\n]*<td.*?><span class=\"style26\"><strong>(Min age)</strong></span></td>\*s<td.*?><span class=\"style26\"><strong>(Max age)</strong></span></td>[\s\r\n]*<td.*?><span class=\"style26\"><strong>(Gender)</strong></span></td>[\s\r\n]*</tr>[\s\r\n]*<tr>[\s\r\n]*<td.*?>(.*?)</td>[\s\r\n]*<td.*?>(.*?)</td>[\s\r\n]*<td.*?>(.*?)</td>[\s\r\n]*<td.*?>(.*?)</td>[\s\r\n]*<td.*?>(.*?)</td>", re.DOTALL | re.IGNORECASE)
	population_match = population_reg.search(text)
	if population_match:
		inclusion = population_match.group(6)
		exclusion = population_match.group(7)
		minage = population_match.group(8)
		maxage = population_match.group(9)
		gender = population_match.group(10)
		elem_values["Inclusion criteria"] = [inclusion]
		elem_values["Exclusion criteria"] = [exclusion]
		elem_values["Age minimum"] = [minage]
		elem_values["Age maximum"] = [maxage]
		elem_values["Gender"] = [gender]
	





		






