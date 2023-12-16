# Create the qubit-Hamiltonian for chemical molecules

from qiskit_nature.units import DistanceUnit
from qiskit_nature.second_q.formats.molecule_info import MoleculeInfo
from qiskit_nature.second_q.drivers import PySCFDriver, Psi4Driver
from qiskit_nature.second_q.mappers import JordanWignerMapper,ParityMapper,BravyiKitaevMapper,QubitMapper
from qiskit.quantum_info import SparsePauliOp

def chemical_model() -> SparsePauliOp:

    mol_info = MoleculeInfo(symbols=['O', 'H'],
                            coords=[[0.0, 0.0, 0.0],[0.45, -0.1525, -0.8454]],
                            charge=1,
                            multiplicity=1)
    
    # On windows, use Psi4Driver
    # On Linux, use PySCFDriver or Psi4Driver
    qmolecule = Psi4Driver.from_molecule(mol_info).run()

    hamiltonian = qmolecule.hamiltonian
    second_q_ham = hamiltonian.second_q_op()
    qubit_ham = JordanWignerMapper().map(second_q_ham)

    print(qubit_ham.num_qubits, "qubits in the Hamiltonian.")

    return qubit_ham
