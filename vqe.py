from qiskit_aer.primitives import Sampler, Estimator
from qiskit.circuit import QuantumCircuit
from qiskit.providers.backend import Backend
from qiskit_aer.noise.noise_model import NoiseModel
from qiskit import transpile
from qiskit.quantum_info import SparsePauliOp

from qiskit_algorithms.minimum_eigensolvers import VQE
from qiskit_algorithms.optimizers import OptimizerResult, COBYLA, SLSQP, L_BFGS_B

from grouping import measurement_circuits_qwc, append_measurement_circuits

from numpy import ndarray, pi, real, random


def initialize_parameters(
    init_params: float | ndarray | list,
    num_params: int,
):
    if isinstance(init_params, float):
        return init_params * random.randn(num_params)
    elif isinstance(init_params, list):
        return ndarray(init_params)
    elif isinstance(init_params, ndarray):
        return init_params

class vqe_ideal:
    """_summary_
    """
    
    def __init__(
        self,
        ansatz: QuantumCircuit,
        init_params: float | ndarray,
        observable: SparsePauliOp,
    ) -> None:
        
        self.circuit = ansatz
        self.init_params = initialize_parameters(init_params, ansatz.num_parameters)
        self.observable = observable
        
        self.counts = []
        self.values = []
        
        return None
        
    def store_intermediate_result(
        self, eval_count, parameters, mean, std
    ):
        self.counts.append(eval_count)
        self.values.append(mean)
        print("iter {0}  \tvalue = {1}".format(eval_count, mean))

    def run(self):
        
        solver = VQE(
            Estimator(),
            self.circuit,
            COBYLA(maxiter=500),
            initial_point=self.init_params,
            callback=self.store_intermediate_result
        )
        
        self.results = solver.compute_minimum_eigenvalue(operator=self.observable)
        
        return self.results



class vqe_with_noise:
    """Variational Quantum Eigensolver
    """
    
    def __init__(
        self,
        ansatz: QuantumCircuit,
        backend: Backend,
        init_params: ndarray,
        observables: list,
        *,
        run_options: dict | None = None,
    ):
        """
        Args:
            ansatz (QuantumCircuit): Ansatz circuit for VQE algorithm
            backend (Backend): Backend of the device, based on which the noise model is automatically created
            init_params (ndarray): Initial parameters of the ansatz circuit
            observables (list): Grouped observables, should be formatted as a list of dictionaries
        """
        
        self.ansatz = ansatz
        self.backend = backend
        self.init_params = initialize_parameters(init_params, ansatz.num_parameters)
        self.observables = observables
        self.num_groups = len(observables)
        
        run_options = {} if run_options is None else run_options
        self.sampler = Sampler(
            backend_options = {
                'method': 'statevector',
                'device': 'CPU',
                'noise_model': NoiseModel.from_backend(backend)
            },
            skip_transpilation=True
        )
        self.sampler.set_options(**run_options)
        
        self.estimator = Estimator(
            backend_options = {
                'method': 'statevector',
                'device': 'CPU',
                'noise_model': NoiseModel.from_backend(backend)
            },
            skip_transpilation=True
        )
        self.estimator.set_options(**run_options)
        
        self.groups = measurement_circuits_qwc(
            self.observables
        )
        
        self.final_circuits = append_measurement_circuits(
            self.ansatz,
            self.groups,
            self.backend
        )
        
        self.counts = []
        self.values = []
        
        
    def fun(
        self, 
        params: ndarray,
    ) -> float:
        
        assigned_circuits = [
            c.assign_parameters(params) for c in self.final_circuits
        ]
        result = self.sampler.run(
            circuits=assigned_circuits
        ).result()

        quasi_dists = result.quasi_dists        
        objective = self.get_expectation(quasi_dists)[0]
        
        count = len(self.counts) + 1
        self.counts.append(count)
        self.values.append(objective)
        
        return objective
        
    def store_intermediate_result(
        self, xk
    ):
        print(f"iter {self.counts[-1]}  \tvalue = {self.values[-1]}")

    def get_expectation(
        self,
        quasi_dists
    ) -> float:
        
        expectation = 0.0

        # Iterate over the circuits (groups)
        for i, g in enumerate(self.groups):
            readouts = list( quasi_dists[i].keys() )
            probs = list( quasi_dists[i].values() )
            
            # Iterate over the observables in the group g
            for j, obs in enumerate(g["observables"]):
                obs_sites = g["measure_sites"][j]
                
                # Iterate over the readouts from the circuits (group g)
                # E.g., if the observable is (IIXY, 0.3), readout is (1101, 0.04),
                #       the contribution to the expectation is 0.3 * 0.04 * (-1)^(0+1) = -0.012,
                #       where (0+1) refers to the last two digits for non-identity terms in the observable
                for k, out_dec in enumerate(readouts):
                    # Convert the readout (stored as decimal) to binary list[int]
                    out_bin = [int(s) for s in list(f"{out_dec:0{self.ansatz.num_qubits}b}")]
                    
                    expectation += real( obs.coeffs * probs[k] * \
                        (-1) ** sum( [out_bin[s] for s in obs_sites] ) )
        
        return expectation
    