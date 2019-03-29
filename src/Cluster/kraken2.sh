#!/bin/bash
#$ -V
#$ -N sequdas_kraken2
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G

python $5/Cluster/kraken2.py $1 $2 $3 $4 $6
