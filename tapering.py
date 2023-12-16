from qiskit.quantum_info import SparsePauliOp
from qiskit.quantum_info.analysis import Z2Symmetries

def Z2_tapering(hamiltonian:SparsePauliOp) -> SparsePauliOp:
    z2sym = Z2Symmetries.find_z2_symmetries(hamiltonian)
    tapered_ham = z2sym.taper(hamiltonian)[0]
    return tapered_ham
