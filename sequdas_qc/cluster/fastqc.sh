#!/bin/bash
#$ -V
#$ -N sequdas_fastqc
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G

python $3/cluster/fastqc.py $1 $2

