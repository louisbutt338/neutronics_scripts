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

materials = ['au', 'al', 'fe', 'in', 'nb', 'ni', 'rh', 'sc', 'y', 'dy', 'cd','cu'] # select materials out of: ss, cu, li,  na, aual, au, al, fe, in, nb, ni, rh, sc, y, dy, cd
ubb_or_other = 'ubb'
projectile = 'neutron' # select: proton neutron
irrad_time = 120 # set irrad time in minutes
no_of_timesteps =  14 #enter number of timesteps used
dose_input = '2 0.3' # 1 or 2 0.3

# note: Set the stoich/mass/density in an original FISPACT {material}.i file. Need input files for each material in /{materials} folder

# for microbreeder flux:
fluxes = [6] # select uBB flux number
approach = '1' # select uBB approach
current_ua = 10 # set the proton current in uA. 
surface_or_cell = 'surface' #state surface or cell or volume
baseline_or_design = 'design2'

image_directory = '/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/' # directory for the plotting
input_filetag = 'uBB' # or uBB

######################
######################
######################
######################

def fispact_setup(volume,material):

    # Sets up the FISPACT file to run - changing the flux normalisation, filename and fluxes file
    input_file_path = shutil.copyfile('/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/materials/experiment/uBB_{}.i'.format(material), '{}_{}_{}{}.i'.format(input_filetag,material,surface_or_cell,volume))
    files_file_path = '/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/files'
    fluxes_file_path = '/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/fluxes/ubb_{}/approach{}/results/results_unshielded/{}_flux/{}_{}_FLUXES.dat'.format(baseline_or_design,approach,projectile,surface_or_cell,volume)
    arb_flux_file_path = '/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/arb_flux'


    with open(fluxes_file_path, 'r') as filename3:
        fluxes_file = filename3.readlines()
    initial_flux_value = float(fluxes_file[185].split()[2])
    print(initial_flux_value)
    fluence_factor = 1.24830e+14/20e-6
    proton_flux = (current_ua*1e-6)*fluence_factor
    final_flux_value = initial_flux_value*proton_flux
    print(final_flux_value)
    if projectile == 'proton':
        with open(arb_flux_file_path,'r') as filename4:
            arb_flux_file = filename4.readlines()
            arb_flux_file[1103:] = fluxes_file
        with open(arb_flux_file_path,'w') as filename4:
            filename4.writelines(arb_flux_file)

    with open(input_file_path,'r') as filename1:
        input_file = filename1.readlines()
    flux_keyword_line = 25+int(input_file[17-1].split()[2])
    input_file[10-1] = '<< ALLDISPEN 40 >> \n'
    input_file[13-1] = '* Approach {} - {} - vol{} - {} flux - {}uA \n'.format(approach,material,volume,projectile,current_ua)
    input_file[flux_keyword_line-6] = 'DOSE {} \n'.format(dose_input)
    input_file[flux_keyword_line-1] = 'FLUX {} \n'.format(final_flux_value)
    input_file[flux_keyword_line+1] = 'TIME {} MINS \n'.format(irrad_time)
    if projectile == 'neutron':
        input_file[5-1] = 'PROJ 1 \n'
        input_file[6-1] = '<< GRPCONVERT 1102 162 >>\n'
        input_file[8-1] = 'GETXS 1 1102 \n'    
    if projectile == 'proton':
        input_file[5-1] = 'PROJ 3 \n'
        input_file[6-1] = 'GRPCONVERT 1102 162 \n'
        input_file[8-1] = 'GETXS 1 162 \n' 
    with open(input_file_path, 'w') as filename1:
        filename1.writelines(input_file)

    with open(files_file_path,'r') as filename2:
        files_file = filename2.readlines()
    if projectile == 'neutron':   
        files_file[5-1] = 'xs_endf ../../nuclear_data/tendl21data/gendf-1102 \n' 
        files_file[8-1] = 'prob_tab  ../../nuclear_data/tendl21data/tp-1102-294 \n'
        files_file[11-1] = 'fluxes {} \n'.format(fluxes_file_path)
        files_file[12-1] = '# arb_flux arb_flux \n'
    if projectile == 'proton':
        files_file[5-1] = 'xs_endf ../../nuclear_data/p-tendl2021/gxs-162 \n'
        files_file[8-1] = 'prob_tab  ../../nuclear_data/tendl21data/tp-1102-294 \n'
        files_file[11-1] = 'fluxes /Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/fluxes/ubb_{}/approach{}/results/{}_flux/volume_{}_fluxes_162.dat \n'.format(baseline_or_design,approach,projectile,volume)
        files_file[12-1] = 'arb_flux arb_flux \n'
    with open(files_file_path, 'w') as filename2:
        filename2.writelines(files_file)
    
def grn_plotter(volume,material):
    
    # Plots the GRN data for the activity in Bq/g and the contact dose in Sv/hr
    with open(os.path.join('/Users/ljb841@student.bham.ac.uk/fispact/WORKSHOP/uBB/{}_{}_{}{}.grn'.format(input_filetag,material,surface_or_cell,volume)),"r") as grn_filename:
        grn_data=grn_filename.readlines()
    timescale=[]
    activity_total = []
    for x in grn_data[8:8+no_of_timesteps]:
        timescale.append(float(x.split()[1]))
        activity_total.append(float(x.split()[3]))
    dose_total = []
    for x in grn_data[36+no_of_timesteps:50+no_of_timesteps]:
        dose_total.append(float(x.split()[3]))
    print('Activity in Bq/g:',1e-3*np.array(activity_total))
    print('Contact dose in Sv/hr:',dose_total)
    timescale_days = np.array(timescale)*365

    #PLOT activity bq/g
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Decay time (days)') 
    ax1.set_ylabel('Activity (Bq/g)')
    ax1.tick_params(axis='y')
    ax1.set_xlim(1e-3,1e3)
    ax1.set_xscale("log")
    #ax1.set_ylim(1e0,1e6)
    ax1.set_yscale("log")
    ax1.plot(timescale_days, 1e-3*np.array(activity_total) , 'k-' ,     linewidth=1.5)
    ax1.axvline(x=0.04167, ls='--', c='grey')
    ax1.axvline(x=1e0, ls='--', c='grey')
    ax1.axvline(x=30, ls='--', c='grey')
    ax1.text(0.2, 1.02, '1 hour', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.text(0.44, 1.02, '1 day', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.text(0.654, 1.02, '1 month', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.grid(which='major')
    #ax1.legend(loc="upper left", bbox_to_anchor=(1, 1), borderaxespad=0, frameon=False, fontsize=11)
    fig.set_size_inches((8, 6))
    fig.savefig(os.path.join(image_directory, 'total_activity_{}_{}{}.png'.format(material,surface_or_cell,volume)), transparent=False, bbox_inches='tight')
    #PLOT ISOTOPIC DOSE
    fig, ax1 = plt.subplots()
    ax1.set_xlabel('Decay time (days)') 
    ax1.set_ylabel('Dose (Sv/h)')
    ax1.tick_params(axis='y')
    ax1.set_xlim(1e-3,1e3)
    ax1.set_xscale("log")
    #ax1.set_ylim(1e-7,1e0)
    ax1.set_yscale("log")
    ax1.plot(timescale_days, (dose_total),'k-' ,    linewidth=1.5)
    ax1.axvline(x=0.04167, ls='--', c='grey')
    ax1.axvline(x=1e0, ls='--', c='grey')
    ax1.axvline(x=30, ls='--', c='grey')
    ax1.text(0.2, 1.02, '1 hour', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.text(0.44, 1.02, '1 day', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.text(0.654, 1.02, '1 month', transform = ax1.transAxes, fontsize=12, c='grey')
    ax1.grid(which='major')
    #ax1.legend(loc="upper left", bbox_to_anchor=(1, 1), borderaxespad=0, frameon=False, fontsize=11)
    fig.set_size_inches((8, 6))
    fig.savefig(os.path.join(image_directory, 'total_dose_{}_{}{}.png'.format(material,surface_or_cell,volume)), transparent=False, bbox_inches='tight')



# Runs FISPACT for all requested volumes    
for i in fluxes:
    for j in materials:
        fispact_setup(str(i),j)
        print('Running FISPACT for {}_{}_{}{}.i'.format(input_filetag,j,surface_or_cell,str(i)))
        os.system('$FISPACT {}_{}_{}{}.i'.format(input_filetag,j,surface_or_cell,str(i)))
        grn_plotter(str(i),j)