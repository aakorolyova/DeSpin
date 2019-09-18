#!python
# -*- coding:utf-8 -*-

'''
Created on 20181123

version 1.0

@author: korolev@limsi.fr, pap@limsi.fr 
'''

# to run call from the directory above this one (../construkt) in a shell:  python construkt

import sys
import glob
import os

#-------

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit()

#-------

from ConstruKT import ConstruKT

# configuration file (for treetagger directory among other things)
# pap@pap-X555YI:/media/pap/HDTOSHIBA1T/work/MIROR/TOOLS/python/constructions/cg_ak4/construkt$ ls -l *.cfg
# -rw-rw-r-- 1 pap pap 78 nov.  26 19:07 ak_datailes_construkt.cfg
# -rw-rw-r-- 1 pap pap 63 nov.  26 19:08 ak_pc_construkt.cfg
# -rw-rw-r-- 1 pap pap 66 nov.  26 19:07 pap_pc_construkt.cfg

app = ConstruKT( config_path = '/media/pap/HDTOSHIBA1T/work/MIROR/TOOLS/python/constructions/cg_ak4/construkt/pap_pc_construkt.cfg' )
app.run()
