#!/usr/bin/env python

"""
Write PNG files for motioncorr and ctf outputs
Rafael Fernandez-Leiro & Nayim Gonzalez-Rodriguez 2022
"""

"""
Activate conda environment before opening relion
Execute from relion gui as external job providing the input micrograph_ctf.star and callyng png_out.py executable
"""

import argparse
import os
import pandas as pd
import starfile
import sys

"""VARIABLES >>>"""
print('running ...')


# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output" , "--o", help = "output folder")
parser.add_argument("-i", "--in_mics", help = "input CTF micrograph starfile")
args, unknown = parser.parse_known_args()

inargs=args.in_mics
outargs=args.output

# Import

print('parsing STAR file...')

try:
    starf_df_optics = starfile.read(inargs)['optics']
    starf_df_mics = starfile.read(inargs)['micrographs']
    apix = starf_df_optics['rlnMicrographPixelSize'].astype(float) ## if more than a single optics group this becomes a series
    data = pd.merge(starf_df_mics, starf_df_optics[['rlnOpticsGroup', 'rlnMicrographPixelSize']], on='rlnOpticsGroup') #SQL like join on Optics group
    files = [(mic, ctf, angpix) for mic, ctf, angpix in zip(data['rlnMicrographName'], data['rlnCtfImage'], data['rlnMicrographPixelSize'])]
except:
    print("No input detected")
    f=open(outargs+"RELION_JOB_EXIT_SUCCESS","w+")
    f.close()    
    exit()

print('writing pngs...')

# Launching relion_image_handler to produce PNG files
start, end = 0, len(files)

for i in files:
    mic, ctf, angpix = i
    os.system(f"if test -f \'{mic[:-3]}png\'; then continue; else `which relion_image_handler` --i {mic} --o {mic[:-3]}png --angpix {angpix} --rescale_angpix {angpix*5} --sigma_contrast 6 --lowpass 10; fi")
    os.system(f"if test -f \'{ctf[:-7]}png\'; then continue; else `which relion_image_handler` --i {ctf} --o {ctf[:-7]}png; fi")
    start += 1
    print(f"Finished {start}/{end}")

print('done!')

### Finish

f=open(outargs+"RELION_JOB_EXIT_SUCCESS","w+")
f.close()
