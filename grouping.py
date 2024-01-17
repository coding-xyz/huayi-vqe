from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp
from qiskit.providers.backend import Backend
from qiskit import transpile
from numpy import pi

def append_measurement_circuits(
    ansatz: QuantumCircuit,
    groups: list[dict],
    backend: Backend,
) -> list[QuantumCircuit]:
    """Append the measuring circuit to the original ansatz

    Args:
        ansatz (QuantumCircuit): Ansatz circuit for VQE algorithm
        groups (list[dict]): Grouped observables with the measurement information
        backend (Backend): Device backend including the noise model

    Returns:
        final_circuits (list[QuantumCircuit]): List of the circuits (for each group) for simulation
    """
    final_circuits = []

    for g in groups:
        circ = ansatz.copy()
        circ.barrier()
        circ = transpile(
            circ.compose(g["measure_circuit"]),
            backend=backend,
            optimization_level=3)
        circ.measure_active()
        final_circuits.append(circ)
    
    return final_circuits

def measurement_circuits_qwc(
    grouped_observables: list[SparsePauliOp]
) -> list[dict]:
    """Get measurement circuits for the grouped observables (qubit-wise only)

    Args:
        grouped_observables (list[SparsePauliOp]): Each element is a SparsePauliOp object with commuting observables

    Returns:
        list[dict]: List of the groups, each contains:
                        observables (SparsePauliOp): Element of the grouped_observables
                        measure_sites (list[list[int]]): List of the indices that should be count
                        measure_gates (str): The gates (Pauli) that should be added to the circuit
                        measure_circuit (QuantumCircuit): The measuring circuit
    """
    
    num_qubits = grouped_observables[0].num_qubits
    groups = []
    
    for g_obs in grouped_observables:
        # g: list of PauliOp in one group
        x0 = [any(g_obs.paulis.x.T[j,:]) for j in range(num_qubits)][::-1]
        z0 = [any(g_obs.paulis.z.T[j,:]) for j in range(num_qubits)][::-1]
        
        # measure_gates: str of the PauliOp that needs to be added to the measurement circuit
        measure_gates = list("I" * num_qubits)
        for j in range(len(measure_gates)):
            if x0[j] and (not z0[j]):
                measure_gates[j] = "X"
            elif (not x0[j]) and z0[j]:
                measure_gates[j] = "Z"
            elif x0[j] and z0[j]:
                measure_gates[j] = "Y"
        
        # measure_sites: list of indeces, each of which should be counted for the measurement of the corresponding PauliOp
        measure_sites = []
        for j in range(len(g_obs)):
            g_str = list(g_obs.paulis.to_labels()[j])
            sites_j = []
            for k in range(num_qubits):
                if g_str[k] == measure_gates[k]:
                    sites_j.append(k)
            measure_sites.append(sites_j)
        
        # measure_circuit: measurement circuit including the rotation gates and measurement operations
        measure_circuit = QuantumCircuit(num_qubits)
        for j in range(len(measure_gates)):
            if measure_gates[j] == 'X':
                measure_circuit.ry(pi/2,j)
            elif measure_gates[j] == 'Y':
                measure_circuit.rx(-pi/2,j)
        
        groups.append({
            "observables":g_obs,
            "measure_sites":measure_sites,
            "measure_gates":"".join(measure_gates),
            "measure_circuit":measure_circuit,
        })
        
    return groups
