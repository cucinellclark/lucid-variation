#!/usr/bin/env snakemake -s

import glob, os

sample_id_list = []
for sample_id in config['single_end_libs']:
    sample_id_list.append(sample_id)
for sample_id in config['paired_end_libs']:
    sample_id_list.append(sample_id)

wildcard_constraints:
    sample_id= '|'.join([re.escape(x) for x in sample_id_list])

rule all:
    input:
        expand("pileup_data/{sample_id}_pileups.table",sample_id=sample_id_list),
        expand("contamination_data/{sample_id}_contamination.table",sample_id=sample_id_list)

rule get_pileup_summary:
    input:
        bam_file="aligned/{sample_id}.bam",
        vcf_file=config['indels'],
        vcf_index=config['indels']
    output:
        pileup_file="pileup_data/{sample_id}_pileups.table"
    shell:
        """
        gatk GetPileupSummaries -I {input.bam_file} -V {input.vcf_file} -L {input.vcf_file} -O {output.pileup_file}
        """

rule calculate_contamination:
    input:
        pileup_file="pileup_data/{sample_id}_pileups.table"
    output:
        contamination_file="contamination_data/{sample_id}_contamination.table"
    shell:
        """
        gatk CalculateContamination -I {input.pileup_file} -O {output.contamination_file}
        """
