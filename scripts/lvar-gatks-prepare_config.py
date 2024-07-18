#!/usr/bin/env python3

import argparse, json
import sys, os

def merge_jsons(j1, j2):
    obj = {}
    for key in j1:
        obj[key] = j1[key]
    for key in j2:
        obj[key] = j2[key]
    return obj

def modify_sample_libs(config):
    if 'single_end_libs' in config:
        sel_dict = {}
        for read_obj in config['single_end_libs']:
            sel_dict[read_obj['sample_id']] = read_obj
        config['single_end_libs'] = sel_dict
    else:
        config['single_end_libs'] = {}
    if 'paired_end_libs' in config: 
        pel_dict = {}
        for read_obj in config['paired_end_libs']:
            pel_dict[read_obj['sample_id']] = read_obj
        config['paired_end_libs'] = pel_dict
    else:
        config['paired_end_libs'] = {}

parser = argparse.ArgumentParser()
parser.add_argument('--job_json',help="Job Json file with samples, reference genome id, conditions, etc",required=True)
parser.add_argument('--config_file',help="Output name for the generated snakemake config file",default='job_config.json')

args = parser.parse_args()

if not os.path.exists(args.job_json):
    print(f"Error, {args.job_json} does not exist, exiting")
    sys.exit()

try:
    with open(args.job_json,'r') as i:
        job_data = json.load(i)
except Exception as e:
    print(f"Error opening json file {args.job_json}, exiting")
    sys.exit()

# check if single/paired reads exist (and condition if diffexp)
# TODO: sra
paired_reads = False
single_reads = False
if 'paired_end_libs' in job_data and len(job_data['paired_end_libs']) > 0:
    paired_reads = True
if 'single_end_libs' in job_data and len(job_data['single_end_libs']) > 0:
    single_reads = True
if not paired_reads and not single_reads:
    print('Reads files not present in job data: exiting')
    sys.exit()

DATA_PATH = os.environ['SERVICE_DATA']
reference_dict = {
    '9606.33': {
        'fasta': f'{DATA_PATH}/Homo_sapiens_assembly38.fasta',
        'dict': f'{DATA_PATH}/Homo_sapiens_assembly38.dict',
        'indels': f'{DATA_PATH}/Homo_sapiens_assembly38.known_indels.vcf.gz',
        'intervals': f'{DATA_PATH}/scattered_calling_intervals',
        'funcotator': f'{DATA_PATH}/funcotator_dataSources.v1.8.hg38.20230908s'
    }
}

job_data = merge_jsons(job_data,reference_dict[job_data['reference_genome_id']])
modify_sample_libs(job_data)

with open(args.config_file,'w') as o:
    json.dump(job_data,o)
