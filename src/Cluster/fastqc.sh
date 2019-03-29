#!/bin/bash
#$ -V
#$ -N sequdas_fastqc
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G

python $3/Cluster/fastqc.py $1 $2

