#!/usr/bin/env python
# circadian_variants_splice_altering.py
"""""""""""""""""""""""""""""""""
# Author: Keila Velazquez-Arcelay
#
# Description: Extract archaic-specific variants in circadian genes, with evidence of having
#              splice-altering effects in at least 1 of the 4 high-coverage archaic genomes.
#              General SAV dataset generated by Colin Brand using SpliceAI predictions.
#
"""""""""""""""""""""""""""""""""


# INPUT DATA
SAVS_FILE = '../data/raw_SpliceAI_circadian_SAVs.tsv'
CIRCADIAN_FILE = '../data/circadian_genes.list'

# OUTPUT DATA
OUTPUT_FILE = '../data/circadian_variants_sav.tsv'


import time
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=pd.core.common.SettingWithCopyWarning)


# LOAD DATA
sav = pd.read_csv(SAVS_FILE, sep='\t')
circadian = pd.read_csv(CIRCADIAN_FILE, sep='\t')


# Extract archaic-specific SAVs
vernot = sav['Vernot_allele_origin']=='archaic-specific'
browning = sav['Vernot_allele_origin']=='archaic-specific'
archaic_sav = sav[vernot | browning]

# Create bed format
archaic_sav.insert(1, 'Start', archaic_sav['pos']-1)
archaic_sav.rename(columns={'chrom':'Chr', 'pos':'End', 'annotation':'GeneName'},inplace=True)
archaic_sav.insert(3, 'Ref/Alt', archaic_sav['ref_allele']+'/'+archaic_sav['alt_allele'])

# Add GeneID
archaic_sav_circadian = pd.merge(archaic_sav, circadian, on='GeneName')

# Filter the columns
keep_cols = ['Chr', 'Start', 'End', 'Ref/Alt', 'GeneID', 'GeneName', 'altai_gt_boolean', 
             'vindija_gt_boolean', 'chagyrskaya_gt_boolean', 'denisovan_gt_boolean']
archaic_sav_circadian = archaic_sav_circadian[keep_cols]

# Convert boolean columns to 1s and 0s
archaic_sav_circadian.iloc[:,6:] = archaic_sav_circadian.iloc[:,6:].applymap(lambda x: 1 if x else 0)

# Fix archaic membership column names
to_capitalize = archaic_sav_circadian.columns[6:].str.replace('_gt_boolean','', regex=True)
capitalized = [col.capitalize() for col in to_capitalize]
archaic_sav_circadian.columns = list(archaic_sav_circadian.columns[:6]) + capitalized

# SORTING
# To prevent the lexicographic sorting of Chr, define the sorting order for that column
chr_order = [f'chr{i}' for i in range(1, 23)] + ['chrX', 'chrY']

# Convert Chr to categorical with the defined sorting order
archaic_sav_circadian['Chr'] = pd.Categorical(archaic_sav_circadian['Chr'], categories=chr_order, ordered=True)

# Sort by Chr and Start
archaic_sav_circadian.sort_values(by=['Chr', 'Start'], inplace=True)


# SAVE DATA
archaic_sav_circadian.to_csv(OUTPUT_FILE, sep='\t', index=False)