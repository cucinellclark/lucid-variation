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
        vcf=expand("vcf_output/{sample_id}.vcf",sample_id=sample_id_list),
        vcf_idx=expand("vcf_output/{sample_id}.vcf.idx",sample_id=sample_id_list),
        filter_vcf=expand("vcf_output/{sample_id}_filtered.vcf.gz",sample_id=sample_id_list)
 
rule unzip_vcf:
    input:
        gzip_vcf="vcf_output/{sample_id}.vcf.gz"
    output:
        vcf = "vcf_output/{sample_id}.vcf"
    shell:
        """
        gunzip {input.gzip_vcf}
        """

rule index_vcf:
    input:
        vcf="vcf_output/{sample_id}.vcf"
    output:
        bai="vcf_output/{sample_id}.vcf.idx"
    log:
        "log/{sample_id}_vcf_index.log"
    shell:
        """
        gatk IndexFeatureFile -I {input.vcf}
        """

rule filter_mutect_vcf:
    input:
        reference=config['fasta'],
        vcf='vcf_output/{sample_id}.vcf'
    output:
        filtered_vcf='vcf_output/{sample_id}_filtered.vcf.gz'
    shell:
        """
        gatk FilterMutectCalls -R {input.reference} -V {input.vcf} -O {output.filtered_vcf}
        """
