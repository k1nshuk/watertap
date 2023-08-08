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
    parameter_sweep,
    ParameterSweep,
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

###############################################################################

def get_sweep_params_simple_old(m, num_samples, scenario="use_LHS"):
    sweep_params = {}

    # Define the sampling type and ranges for three different variables
    if scenario == "use_LHS":
        sweep_params["A_comp"] = LatinHypercubeSample(
            m.fs.RO.A_comp, 0.5e-12, 5e-12, num_samples
        )

    elif scenario == "RandomSampling":
        sweep_params["A_comp"] = NormalSample(
            m.fs.RO.A_comp, 4.0e-12, 0.5e-12, num_samples
        )
        sweep_params["B_comp"] = NormalSample(
            m.fs.RO.B_comp, 3.5e-8, 0.5e-8, num_samples
        )

    elif scenario == "FixedSampling":
        sweep_params["A_comp"] = LinearSample(
            m.fs.RO.A_comp, 1.0e-12, 1e-11, num_samples
        )
        # sweep_params["B_comp"] = LinearSample(
        #     m.fs.RO.B_comp, 3.5e-8, 0.5e-8, num_samples
        # )
    else:
        pass
        # raise NotImplementedError

    return sweep_params

def get_sweep_params_recursive_old(m, num_samples, scenario="RandomSampling"):
    sweep_params = {}

    # Define the sampling type and ranges for three different variables
    if scenario == "RandomSampling":
        sweep_params["A_comp"] = NormalSample(
            m.fs.RO.A_comp, 4.0e-12, 0.5e-12, num_samples
        )
        sweep_params["B_comp"] = NormalSample(
            m.fs.RO.B_comp, 3.5e-8, 0.5e-8, num_samples
        )
        sweep_params["cost"] = UniformSample(
            m.fs.costing.reverse_osmosis.membrane_cost, 10, 50, num_samples
        )  # Show distribution of cost
    else:
        pass
        # raise NotImplementedError

    return sweep_params

###############################################################################

def get_sweep_params_simple(m, scenario="use_LHS"):
    sweep_params = {}

    # Define the sampling type and ranges for three different variables
    if scenario == "A_comp_vs_LCOW":
        num_samples = 100
        sweep_params["A_comp"] = LinearSample(
            m.fs.RO.A_comp, 1.0e-12, 1e-11, num_samples
        )

    elif scenario == "WR_vs_NaCL_loading_vs_LCOW":
        num_samples = 10
        sweep_params["recovery"] = LinearSample(
            m.fs.RO.recovery_mass_phase_comp[0, "Liq", "H2O"], 0.1, 0.65, num_samples
        )
        sweep_params["NaCl_loading"] = LinearSample(
            m.fs.feed.properties[0].flow_mass_phase_comp["Liq", "NaCl"], 
            0.01, 0.05, num_samples
        )

    elif scenario == "A_comp_vs_B_comp_vs_LCOW":
        num_samples = 10
        sweep_params["A_comp"] = LinearSample(
            m.fs.RO.A_comp, 1.0e-12, 1e-11, num_samples
        )
        sweep_params["B_comp"] = LinearSample(
            m.fs.RO.B_comp, 8.0e-8, 1.0e-8, num_samples
        )
    elif scenario == "Scaling_Study":
        num_samples = 1e5
        sweep_params["A_comp"] = UniformSample(
            m.fs.RO.A_comp, 1.0e-12, 1e-11, num_samples
        )
        sweep_params["B_comp"] = UniformSample(
            m.fs.RO.B_comp, 8.0e-8, 1.0e-8, num_samples
        )
        sweep_params["ERD_efficiency"] = UniformSample(
            m.fs.P2.efficiency_pump, 0.95, 0.99, num_samples
        ) # Is this the correct pyomo variable?
    else:
        pass
        # raise NotImplementedError

    return sweep_params, num_samples

def get_sweep_params_differential(m):
    num_samples = 1000
    sweep_params = {}
    differential_sweep_specs = {}

    # Do not do NaCl loading
    # sweep_params["NaCl_loading"] = LinearSample(
    #     m.fs.feed.properties[0].flow_mass_phase_comp["Liq", "NaCl"], 
    #     0.01, 0.05, num_samples
    # )
    # DO membrane cost
    # Pr
    # sweep_params["Spacer_porosity"] = UniformSample(
    #     m.fs.RO.feed_side.spacer_porosity, 0.95, 0.99, num_samples
    # )

    # Only improve A_comp
    sweep_params["A_comp"] = UniformSample(
        m.fs.RO.A_comp, 4.2e-12, 2.1e-11, num_samples
    )
    sweep_params["membrane_cost"] = UniformSample(
        m.fs.costing.reverse_osmosis.membrane_cost, 30, 10, num_samples
    )
    sweep_params["px_cost"] = UniformSample(
        m.fs.costing.pressure_exchanger.cost, 535, 250, num_samples
    )
    sweep_params["px_efficiency"] = UniformSample(
        m.fs.PXR.efficiency_pressure_exchanger, 0.95, 0.99, num_samples
    )

    differential_sweep_specs["A_comp"] = {
        "diff_sample_type": UniformSample,
        "diff_mode": "percentile",
        "nominal_lb" : sweep_params["A_comp"].lower_limit,
        "nominal_ub" : sweep_params["A_comp"].upper_limit,
        "relative_lb" : 0.05,
        "relative_ub" : 0.05,
        "pyomo_object": m.fs.RO.A_comp,
    }

    differential_sweep_specs["membrane_cost"] = {
        "diff_sample_type": UniformSample,
        "diff_mode": "percentile",
        "nominal_lb" : sweep_params["membrane_cost"].lower_limit,
        "nominal_ub" : sweep_params["membrane_cost"].upper_limit,
        "relative_lb" : -0.05,
        "relative_ub" : -0.05,
        "pyomo_object": m.fs.costing.reverse_osmosis.membrane_cost,
    }

    differential_sweep_specs["px_cost"] = {
        "diff_sample_type": UniformSample,
        "diff_mode": "percentile",
        "nominal_lb" : sweep_params["px_cost"].lower_limit,
        "nominal_ub" : sweep_params["px_cost"].upper_limit,
        "relative_lb" : -0.05,
        "relative_ub" : -0.05,
        "pyomo_object": m.fs.costing.pressure_exchanger.cost,
    }

    differential_sweep_specs["px_efficiency"] = {
        "diff_sample_type": UniformSample,
        "diff_mode": "percentile",
        "nominal_lb" : sweep_params["px_efficiency"].lower_limit,
        "nominal_ub" : sweep_params["px_efficiency"].upper_limit,
        "relative_lb" : 0.02,
        "relative_ub" : 0.02,
        "pyomo_object": m.fs.PXR.efficiency_pressure_exchanger,
    }


    return num_samples, sweep_params, differential_sweep_specs


def run_parameter_sweep(
    run_type,
    scenario="RandomSampling",
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

    import pprint
    # pprint.pprint(m.display())

    # Simulate once outside the parameter sweep to ensure everything is appropriately initialized
    solve(m, solver=solver)

    # Run the parameter sweep study using num_samples randomly drawn from the above range
    
    # Define the outputs to be saved
    outputs = {}
    outputs["EC"] = m.fs.costing.specific_energy_consumption
    outputs["LCOW"] = m.fs.costing.LCOW

    if run_type == "simple":
        sweep_params, num_samples = get_sweep_params_simple(m, scenario=scenario)
        ps = ParameterSweep(
            csv_results_file_name=csv_results_file_name,
            h5_results_file_name=f"output/results_{run_type}_{scenario}_{num_samples}.h5",
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
    elif run_type == "differential":
        num_samples, sweep_params, differential_sweep_specs = get_sweep_params_differential(m)
        _, global_results_dict = differential_parameter_sweep(
            m,
            sweep_params,
            differential_sweep_specs,
            outputs=outputs,
            csv_results_file_name=csv_results_file_name,
            h5_results_file_name=f"output/results_{run_type}_{num_samples}.h5",
            optimize_function=optimize,
            optimize_kwargs={"solver": solver, "check_termination": False},
            num_samples=num_samples,
            num_diff_samples=1,
            seed=seed,
        )
    else:
        raise NotImplementedError

    

    return global_results_dict


if __name__ == "__main__":

    # For testing this file, a seed needs to be provided as an additional argument, i.e. seed=1
    run_type_dict = {
        # "simple" : ["WR_vs_NaCL_loading_vs_LCOW"], # ["WR_vs_Salinity_vs_LCOW"] # ["A_comp_vs_B_comp_vs_LCOW"],
        "differential" : ["UniformSampling"],
    }
    # num_samples = 100
    results_dict = {}

    for run_type, scenarios in run_type_dict.items():
        results_dict[run_type] = {}
        for scenario in scenarios:
            results_dict[run_type][scenario] = run_parameter_sweep(
                run_type,
                scenario=scenario,
            )
        #     break
        # break

    # import pprint
    # pprint.pprint(global_results_dict)
