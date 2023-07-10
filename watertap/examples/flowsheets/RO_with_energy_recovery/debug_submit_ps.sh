#!/bin/bash 
#SBATCH --nodes=2  # Run the tasks on the same node
#SBATCH --ntasks-per-node=36 # Tasks per node to be run
#SBATCH --time=0:20:00   # Required, estimate 5 minutes
#SBATCH --account=watertap # Required
#SBATCH --partition=debug
#SBATCH --mail-user=kinshuk.panda@nrel.gov
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE

cd /projects/watertap/kpanda/watertap/watertap/examples/flowsheets/RO_with_energy_recovery/
module load conda/4.9.2
module load openmpi/4.1.0/gcc-8.4.0
source activate /projects/watertap/kpanda/conda-envs/watertap

NUM_SAMPLES=1000

srun -n 72 -N 2 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_72 2> errout_72
srun -n 36 -N 1 --ntasks-per-node=36 python tr_scaling.py $NUM_SAMPLES > fout_36 2> errout_36
