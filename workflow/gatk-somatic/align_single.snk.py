#!/usr/bin/env snakemake -s

import os

sample_id_list = []
for sample_id in config['single_end_libs']:
    sample_id_list.append(sample_id)

wildcard_constraints:
    sample_id= '|'.join([re.escape(x) for x in sample_id_list])

rule all:
    input:
        expand("aligned/{sample_id}.bam", sample_id=sample_id_list),
        expand("aligned/{sample_id}.bam.bai", sample_id=sample_id_list)

rule minimap2_alignment_single:
    input:
    output:
        aligned_read = 'aligned/{sample_id}.bam'
    params:
        preset = 'sr', # sr stands for short-read
        fasta = config['fasta'],
        read = lambda wildcards: config['single_end_libs'][wildcards.sample_id]['read'],
    threads: 4
    log:
        "log/{sample_id}_minimap2.log"
    shell:
        """
        cmd="minimap2 -ax {params.preset} -t {threads} {params.fasta} {params.read} -R "@RG\\tID:{wildcards.sample_id}\\tPL:ILLUMINA\\tLB:LB1\\tSM:{wildcards.sample_id}" | \
        samtools sort -o {output.aligned_read} -"
        echo $cmd
        """ 

rule index_bam:
    input:
        bam="aligned/{sample_id}.bam"
    output:
        bai="aligned/{sample_id}.bam.bai"
    log:
        "log/{sample_id}_index.log"
    shell:
        """
        samtools index {input.bam} {output.bai}
        """