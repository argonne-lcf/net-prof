#!/bin/bash -x
#PBS -A datascience
#PBS -k doe
#PBS -l select=1:ncpus=208
#PBS -q debug
#PBS -l walltime=00:15:00
#PBS -l filesystems=flare

cd $PBS_O_WORKDIR
echo "Job started at: $(date)"
echo "Job ID: $PBS_JOBID"
echo "Working directory: $PBS_O_WORKDIR"
echo "Node list:"
cat $PBS_NODEFILE

NNODES=`wc -l < $PBS_NODEFILE` 
RANKS_PER_NODE=1
NRANKS=$(( NNODES * RANKS_PER_NODE ))
DATE=`date | tr ' :+' '__' `

mpiexec -n ${NNODES} -ppn ${RANKS_PER_NODE} bash -O extglob -c 'cat /sys/class/cxi/cxi*/device/telemetry/!(ALL-in-binary) > '/tmp/cxi_metric_${DATE}' '

# Run again to collect after metrics
