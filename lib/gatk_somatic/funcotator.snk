#!/usr/bin/env snakemake -s

import os,re

sample_id_list = []
for sample_id in config['single_end_libs']:
    sample_id_list.append(sample_id)
for sample_id in config['paired_end_libs']:
    sample_id_list.append(sample_id)

wildcard_constraints:
    sample_id= '|'.join([re.escape(x) for x in sample_id_list])

rule all:
    input:
        maft=expand("funcotator/{sample_id}.maf",sample_id=sample_id_list)

rule funcotator:
    input:
        reference=config['fasta'],
        vcf='vcf_output/{sample_id}_filtered.vcf.gz'
    output:
        outfile='funcotator/{sample_id}.maf'
    params:
        func_db=config['funcotator']
    shell:
        """
        gatk Funcotator -R {input.reference} -V {input.vcf} -O {output.outfile} --output-file-format MAF --data-sources-path {params.func_db} --ref-version hg38
        """
