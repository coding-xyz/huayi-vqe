from qiskit.circuit import QuantumCircuit
from qiskit.quantum_info import SparsePauliOp

def grouping_observables(circ_hardware:QuantumCircuit,
                         hamiltonian:SparsePauliOp, 
                         grouping_method=SparsePauliOp.group_commuting) \
                            -> list[SparsePauliOp]:
    
    def rerange(op, maptable):
        num_qubits_device = circ_hardware.num_qubits
        num_qubits_op = len(op)
        newstr = list('I'*num_qubits_device)
        for k,v in maptable.items():
            # newstr[v] = op[k]
            newstr[num_qubits_device-1-v] = op[num_qubits_op-1-k] # why reverse its order? according to Fudan's group
        return ''.join(newstr)
        
    grouped_ham = grouping_method(hamiltonian)

    qubits = circ_hardware.layout.initial_layout.get_virtual_bits()
    maptable = {}
    for q in qubits:
        if 'ancilla' not in q.register.name:
            maptable[q.index] = qubits[q]
    
    grouped_observables = []
    for partial_ham in grouped_ham:
        ops = []
        for h in partial_ham:
            op = h.paulis.to_labels()[0]
            ops.append(rerange(op, maptable))
        grouped_observables.append(SparsePauliOp(ops, partial_ham.coeffs))

    return grouped_observables