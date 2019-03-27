#!/bin/bash
#$ -V
#$ -N sequdas_coverage
#$ -cwd
#$ -pe smp 25
#$ -l h_vmem=100G

python $6/Cluster/coverage.py $1 $2 $3 $4 $5