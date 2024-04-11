import os
import shutil
import numpy as np
import sys
import matplotlib.font_manager
import matplotlib
import matplotlib.pyplot as plt
#from sklearn.linear_model import LinearRegression
from scipy.stats import gaussian_kde
import seaborn
#plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = "Helvetica"
plt.rcParams["font.size"] = 22
plt.rcParams["font.weight"] = "normal"
from collections import Counter
from itertools import count
from random import randint
from pathlib import Path
import math

######################
######################
######################
######################

fluxes = ['1','2','3'] # select flux number
materials = ['fe'] # select materials out of: ss, cu, li,  na, aual, au, al, fe, in, nb, ni, rh, sc, y
approach = '1' # select uBB approach
projectile = 'neutron' # select: proton neutron
current_ua = 1 # set the proton current in uA. 
surface_or_cell = 'surface'
fluxes_energies = 'mev'
number_pkas_used = 4

# note: Set the stoich/mass/density in an original FISPACT {material}.i file. Need input files for each material in /{materials} folder

image_directory = '/Users/ljb841@student.bham.ac.uk/SPECTRA-PKA/manual/workshop_pka/uBB/' # directory for the plotting

######################
######################
######################
######################

def spectra_setup(volume,material):

    # Sets up the FISPACT file to run - changing the flux normalisation, filename and fluxes file
    input_file_path = shutil.copyfile('/Users/ljb841@student.bham.ac.uk/SPECTRA-PKA/manual/workshop_pka/uBB/materials/uBB_{}.in'.format(material), 'uBB_{}_approach{}_{}{}_{}uA.in'.format(material,approach,surface_or_cell,volume,str(current_ua)))
    fluxes_file_path = '/Users/ljb841@student.bham.ac.uk/SPECTRA-PKA/manual/workshop_pka/fluxes/ubb_approach{}_{}{}.dat'.format(approach,surface_or_cell,volume)

    fluence_factor = 1.24830e+14/20
    proton_flux_factor = current_ua*fluence_factor

    with open(input_file_path,'r') as filename1:
        input_file = filename1.readlines()
#    number_pkas_used = [*str(input_file[16-1].split())]
    flux_keyword_line = 4+int(number_pkas_used)
    input_file[0] = 'flux_filename="{}" \n'.format(fluxes_file_path)
    input_file[1] = 'results_stub="uBB_{}_approach{}_{}{}_{}uA" \n'.format(material,approach,surface_or_cell,volume,str(current_ua))
    if fluxes_energies == 'mev':
        input_file[flux_keyword_line+8] = 'flux_energy_rescale_value=1 \n'
    if fluxes_energies == 'ev':
        input_file[flux_keyword_line+8] = 'flux_energy_rescale_value=1e-6 \n'
    input_file[flux_keyword_line+9] = 'flux_rescale_value={} \n'.format(proton_flux_factor)
    with open(input_file_path, 'w') as filename1:
        filename1.writelines(input_file)

# Runs FISPACT for all requested volumes    
for i in fluxes:
    for j in materials:
        spectra_setup(str(i),j)
        print('Running Spectra-PKA for uBB_{}_approach{}_{}{}_{}uA.in'.format(j,approach,surface_or_cell,i,str(current_ua)))
        os.system('$SPECTRA_PKA uBB_{}_approach{}_{}{}_{}uA.in'.format(j,approach,surface_or_cell,i,str(current_ua)))