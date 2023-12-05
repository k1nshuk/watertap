#################################################################################
# WaterTAP Copyright (c) 2020-2023, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory, Oak Ridge National Laboratory,
# National Renewable Energy Laboratory, and National Energy Technology
# Laboratory (subject to receipt of any required approvals from the U.S. Dept.
# of Energy). All rights reserved.
#
# Please see the files COPYRIGHT.md and LICENSE.md for full copyright and license
# information, respectively. These files are also available online at the URL
# "https://github.com/watertap-org/watertap/"
#################################################################################

from idaes.core.solvers import get_solver
from watertap.tools.parameter_sweep import (
    UniformSample,
    NormalSample,
    LatinHypercubeSample,
    LinearSample,
    GeomSample,
    ReverseGeomSample,
    ParameterSweep,
    parameter_sweep,
    recursive_parameter_sweep,
    differential_parameter_sweep,
)

from watertap.examples.flowsheets.RO_with_energy_recovery.RO_with_energy_recovery import (
    build,
    set_operating_conditions,
    initialize_system,
    solve,
    optimize,
)

from watertap.tools.parameter_sweep import (
    get_sweep_params_from_yaml,
    set_defaults_from_yaml,
)

def get_sweep_params(m, num_samples):

    sweep_params = {}
    sweep_params["A_comp"] = UniformSample(
        m.fs.RO.A_comp, 1.0e-12, 1e-11, num_samples
    )
    sweep_params["NaCl_loading"] = UniformSample(
        m.fs.feed.properties[0].flow_mass_phase_comp["Liq", "NaCl"], 
        0.01, 0.05, num_samples
    )
    sweep_params["ERD_cost"] = NormalSample(
        m.fs.costing.pressure_exchanger.cost, 535, 60, num_samples
    )

    return sweep_params

def run_parameter_sweep(
    comm_size,
    num_samples=10,
    csv_results_file_name=None,
    h5_results_file_name=None,
    seed=None,
):

    # Set up the solver
    solver = get_solver()

    # Build, set, and initialize the system (these steps will change depending on the underlying model)
    m = build()
    set_operating_conditions(m, water_recovery=0.5, over_pressure=0.3, solver=solver)
    initialize_system(m, solver=solver)

    # Simulate once outside the parameter sweep to ensure everything is appropriately initialized
    solve(m, solver=solver)

    # Run the parameter sweep study using num_samples randomly drawn from the above range
    
    # Define the outputs to be saved
    outputs = {}
    outputs["EC"] = m.fs.costing.specific_energy_consumption
    outputs["LCOW"] = m.fs.costing.LCOW

    
    sweep_params = get_sweep_params(m, num_samples)
    # # Run the parameter sweep
    # _, global_results_dict = parameter_sweep(
    #     m,
    #     sweep_params,
    #     outputs=outputs,
    #     csv_results_file_name=csv_results_file_name,
    #     h5_results_file_name=f"output/scaling/results_scaling_{comm_size}_{num_samples}.h5",
    #     optimize_function=optimize,
    #     optimize_kwargs={"solver": solver, "check_termination": False},
    #     reinitialize_function=initialize_system,
    #     reinitialize_kwargs={"solver": solver},
    #     reinitialize_before_sweep=False,
    #     num_samples=num_samples,
    #     seed=seed,
    # )
    ps = ParameterSweep(
            csv_results_file_name=csv_results_file_name,
            h5_results_file_name=f"output/scaling/results_scaling_{comm_size}_{num_samples}.h5",
            optimize_function=optimize,
            optimize_kwargs={"solver": solver, "check_termination": False},
            reinitialize_function=initialize_system,
            reinitialize_kwargs={"solver": solver},
            reinitialize_before_sweep=False,
        )
    _, global_results_dict = ps.parameter_sweep(
        m,
        sweep_params,
        combined_outputs=outputs,
        num_samples=num_samples,
        seed=seed,
    )
    
    return ps, global_results_dict

if __name__ == "__main__":

    import time
    import sys
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    comm_size = comm.Get_size()

    start_time = time.time()
    if len(sys.argv) == 1:
        num_samples = 10
    else:
        num_samples = int(sys.argv[1])
    
    ps, result_dict =  run_parameter_sweep(
        comm_size,
        num_samples=num_samples
    )
    comm.Barrier()
    end_time = time.time()
    time_elapsed = end_time - start_time

    if ps.parallel_manager.is_root_process():
        print("ps.time_building_combinations = ", ps.time_building_combinations)
        print("ps.time_sweep_solves = ", ps.time_sweep_solves)
        print("ps.time_gathering_results = ", ps.time_gathering_results)
        print("ps.time_writing_files = ", ps.time_writing_files)
        print("time_elapsed = ", time_elapsed)

    comm.Barrier()