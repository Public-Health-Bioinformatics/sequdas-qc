#!/bin/bash
#$ -V
#$ -N sequdas_coverage
#$ -cwd
#$ -pe smp 7
#$ -l h_vmem=100G

python $6/cluster/coverage.py $1 $2 $3 $4 $5