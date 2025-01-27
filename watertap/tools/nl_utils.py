import os
import watertap

def serialize(m, fname, type="nl"):

    if type == "nl":
        m.write(
            os.path.join(
                os.path.dirname(watertap.__file__),
                "nl_files",
                fname
            ), 
            io_options={"symbolic_solver_labels":True}
        )
    elif type == "gms":
        m.write(
            os.path.join(
                os.path.dirname(watertap.__file__),
                "gms_files",
                fname
            ), 
            io_options={"symbolic_solver_labels":True}
        )
    else:
        raise NotImplementedError
    