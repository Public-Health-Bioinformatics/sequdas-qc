#!/bin/bash
#$ -V
#$ -N sequdas_krona
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G

python $6/Cluster/krona.py $1 $2 $3 $4 $5 $7 $6