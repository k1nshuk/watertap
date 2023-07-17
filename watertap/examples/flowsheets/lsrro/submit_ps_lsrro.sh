#!/bin/bash 
#SBATCH --nodes=6  # Run the tasks on the same node
#SBATCH --ntasks-per-node=36 # Tasks per node to be run
#SBATCH --time=2:30:00   # Required, estimate 5 minutes
#SBATCH --account=watertap # Required
#SBATCH --partition=short
#SBATCH --qos=normal
#SBATCH --mail-user=kinshuk.panda@nrel.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE

cd /projects/watertap/kpanda/watertap/watertap/examples/flowsheets/lsrro/
module load conda/4.9.2
module load openmpi/4.1.0/gcc-8.4.0
source activate /projects/watertap/kpanda/conda-envs/watertap

NUM_SAMPLES=100

srun -n 180 -N 5 --ntasks-per-node=36 python multi_sweep_scaling.py $NUM_SAMPLES > fout_180 2> errout_180
srun -n 144 -N 4 --ntasks-per-node=36 python multi_sweep_scaling.py $NUM_SAMPLES > fout_144 2> errout_144

srun -n 108 -N 3 --ntasks-per-node=36 python multi_sweep_scaling.py $NUM_SAMPLES > fout_108 2> errout_108 &
srun -n 72 -N 2 --ntasks-per-node=36 python multi_sweep_scaling.py $NUM_SAMPLES > fout_72 2> errout_72 &
srun -n 36 -N 1 --ntasks-per-node=36 python multi_sweep_scaling.py $NUM_SAMPLES > fout_36 2> errout_36 &

wait
