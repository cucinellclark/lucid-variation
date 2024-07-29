import argparse
import json
import os
import sys
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument('-c','--config',required=True)

args = parser.parse_args()

with open(args.config,'r') as i:
    config = json.load(i)

reads_libs = list(config['single_end_libs'].values()) + list(config['paired_end_libs'].values())

# assuming it will be each sample condition vs control
condition_dict = {}
bam_dict = {}
for read_obj in reads_libs:
    cond = read_obj['condition']
    if cond not in condition_dict:
        condition_dict[cond] = []
    sample_id = read_obj['sample_id']
    condition_dict[cond].append(read_obj['sample_id'])
    bam_file = os.path.join('aligned',f'{sample_id}.bam')
    bam_dict[read_obj['sample_id']] = bam_file

if not 'control' in condition_dict:
    sys.stderr.write("Required control condition not present, exiting\n")
    sys.exit(-1)

data_list = []
control_bams = []
for sample_id in condition_dict['control']:
    control_bams.append(bam_dict[sample_id])
for cond in condition_dict:
    if cond == 'control':
        continue
    for sample_id in condition_dict[cond]:
        sample_bam = bam_dict[sample_id]
        output = f'{sample_id}.bcf'
        data = [output,cond,'control',sample_bam,','.join(control_bams)]
        data_list.append(data)

data_df = pd.DataFrame(data_list)
data_df.columns = ['Output','Condition','Control','ConditionBam','ControlBams']

data_df.to_csv('delly_sample_table.txt',sep='\t',index=False)
