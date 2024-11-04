#!/usr/bin/env python3

import os, sys, glob, argparse
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--threads','-t',help='number of threads to use for tools',default='4')
parser.add_argument('--config','-c',help='config file for snakemake file',default="job_config.json")

args = parser.parse_args()
print(args)

with open(args.config,'r') as i:
    config = json.load(i)

config_path = os.path.realpath(args.config)

# workflow_dir is workflow folder + recipe
workflow_dir = os.path.join(config['workflow_dir'],'gatk-somatic')
struct_dir = os.path.join(config['workflow_dir'],'structural-variation')

print(config)
single_end = []
paired_end = []
error = False
file_dict = {}
if 'single_end_libs' in config:
    single_end = config['single_end_libs']
if 'paired_end_libs' in config:
    paired_end = config['paired_end_libs']
for sample_id in single_end:
    if not os.path.exists(single_end[sample_id]['read']):
        error = True
        print(f'{single_end[sample_id]["read"]} does not exist')
for sample_id in paired_end:
    if not os.path.exists(paired_end[sample_id]['read1']):
        error = True
        print(f'{paired_end[sample_id]["read1"]} does not exist')
if error:
    print('fix file issues')
    sys.exit()

### create output directory and file and change into it
# TODO: change?
if not os.path.exists(config["output_path"]):
    print(f'Output directory {config["output_path"]} doesnt exist, exiting')
    sys.exit()
output_folder = os.path.join(config["output_path"],config["output_file"])
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
os.chdir(output_folder)

### Run alignment
# - all output necessary for downstream programs should be put into the aligned directory
if False and len(paired_end) > 0:
    # run paired snakemake
    try:
        snkfile = os.path.join(workflow_dir,'align_paired.snk')
        cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c','12','--nolock']
        print(' '.join(cmd))
        subprocess.check_call(cmd)
    except Exception as e:
        print(f'Error running paired snakemake:\n{e}\n')
        sys.exit()
if len(single_end) > 0:
    # run single snakemake
    try:
        snkfile = os.path.join(workflow_dir,'align_single.snk')
        cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c',args.threads]
        print(' '.join(cmd))
        subprocess.check_call(cmd)
    except Exception as e:
        print(f'Error running single snakemake:\n{e}\n')
        sys.exit()

try:
    snkfile = os.path.join(workflow_dir,'mutect2.snk')
    cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c','4']
    print(' '.join(cmd))
    subprocess.check_call(cmd)
except Exception as e:
    print(f'Error running snakemake mutect2:\n{e}\n')
    sys.exit()

try:
    snkfile = os.path.join(workflow_dir,'pileup_contamination.snk') 
    cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c','4']
    print(' '.join(cmd))
    subprocess.check_call(cmd)
except Exception as e:
    print(f'Error running snakemake pileup and contamination:\n{e}\n')
    sys.exit()

try:
    snkfile = os.path.join(workflow_dir,'process_vcf.snk')
    cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c','4']
    print(' '.join(cmd))
    subprocess.check_call(cmd)
except Exception as e:
    print(f'Error running snakemake process vcf:\n{e}\n')
    sys.exit()

try:
    snkfile = os.path.join(workflow_dir,'funcotator.snk')
    cmd = ['snakemake','-s',snkfile,'--configfile',config_path,'-c','4','--rerun-incomplete']
    print(' '.join(cmd))
    subprocess.check_call(cmd)
except Exception as e:
    print(f'Error running snakemake funcotator:\n{e}\n')
    sys.exit()

### Strucutral variation tools
if config['run_delly']:
    prep_delly = os.path.join(struct_dir,'prepare_structvar_config.py')
    prep_cmd = ['python3',prep_delly,'-c',config_path]
    print(' '.join(prep_cmd))
    subprocess.check_call(prep_cmd)
    try:
        snkfile_delly = os.path.join(struct_dir,'delly.snk')
        delly_cmd = ['snakemake','-s',snkfile_delly,'--configfile',config_path,'-c','4']
        print(' '.join(delly_cmd))
        subprocess.check_call(delly_cmd)
    except Exception as e:
        print(f'Error running snakemake delly:\n{e}\n')
        sys.exit()
    try:
        snkfile_manta = os.path.join(struct_dir,'manta.snk')
        manta_cmd = ['snakemake','-s',snkfile_manta,'--configfile',config_path,'-c','4']
        print(' '.join(manta_cmd))
        subprocess.check_call(manta_cmd)
    except Exception as e:
        print(f'Error running snakemake manta:\n{e}\n')
        sys.exit()

### sigprofileextractor 
try:
    snkfile_sigpro = os.path.join(workflow_dir,'sigProfileExtractor.snk')
    sigpro_cmd = ['snakemake','-s',snkfile_sigpro,'--configfile',config_path,'-c','4']
    print(' '.join(sigpro_cmd))
    subprocess.check_call(sigpro_cmd)
except Exception as e:
    print(f'Error running snakemake sigProfileExtractor:\n{e}\n')
    sys.exit()
