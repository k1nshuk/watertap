#!/bin/bash 
#SBATCH --ntasks=180 # Tasks to be run
#SBATCH --nodes=5  # Run the tasks on the same node
#SBATCH --time=4:00:00   # Required, estimate 5 minutes
#SBATCH --account=watertap # Required
#SBATCH --partition=short

cd /projects/watertap/kpanda/watertap/watertap/examples/flowsheets/RO_with_energy_recovery/
module load conda/4.9.2
module load openmpi/4.1.0/gcc-8.4.0
source activate /projects/watertap/kpanda/conda-envs/watertap

NUM_SAMPLES=1000

srun -n 180 -N 5 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_180 2> errout_180
srun -n 144 -N 4 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_144 2> errout_144

srun -n 108 -N 3 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_144 2> errout_144 &
srun -n 72 -N 2 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_144 2> errout_144 &

wait
