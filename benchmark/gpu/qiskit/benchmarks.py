

import pytest
import numpy as np
import uuid
from qiskit import Aer, QuantumCircuit, execute
from qiskit.compiler import transpile, assemble

max_parallel_threads = 16
gpu = True
method = "statevector" if not gpu else "statevector_gpu"


def native_execute(benchmark, circuit, fusion_enable, include_compile_time):
    backend_options = {
        "method": method,
        "precision": "double",
        "max_parallel_threads": max_parallel_threads,
        "truncate_enable": False,
        "fusion_enable": True,
        "fusion_threshold": 14,
        "fusion_max_qubit": 5,
    }
    if not fusion_enable:
        backend_options["fusion_enable"] = False
        backend_options["fusion_threshold"] = 30
        backend_options["fusion_max_qubit"] = 0

    backend = Aer.get_backend("statevector_simulator")
    backend.set_options(**backend_options)

    def evalfunc_include(backend, circuit, backend_options):
        experiment = transpile(circuit, backend=backend)
        qobj = assemble(experiment, backend=backend, shot=1, memory_slot_size=100)
        qobj_aer = backend._format_qobj(qobj, backend_options)
        qobj_dict = qobj_aer.to_dict()
        backend._controller(qobj_dict)

    def evalfunc_exclude(backend, qobj_dict):
        backend._controller(qobj_dict)

    if include_compile_time:
        benchmark(evalfunc_include, backend, circuit, backend_options)
    else:
        experiment = transpile(circuit, backend=backend)
        qobj = assemble(experiment, backend=backend, shot=1, memory_slot_size=100)
        qobj_aer = backend._format_qobj(qobj, backend_options)
        qobj_dict = qobj_aer.to_dict()
        benchmark(evalfunc_exclude, backend, qobj_dict)


def first_rotation(circuit, nqubits):
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def mid_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def last_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    return circuit


def entangler(circuit, pairs):
    for a, b in pairs:
        circuit.cx(a, b)
    return circuit


def generate_qcbm_circuit(nqubits, depth, pairs):
    circuit = QuantumCircuit(nqubits)
    first_rotation(circuit, nqubits)
    entangler(circuit, pairs)
    for k in range(depth - 1):
        mid_rotation(circuit, nqubits)
        entangler(circuit, pairs)
    last_rotation(circuit, nqubits)
    return circuit


nqubit_list = range(4, 26)


"""
@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_gf_inc(benchmark, nqubits):
    benchmark.group = "QCBMoptinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=True, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_gf_exc(benchmark, nqubits):
    benchmark.group = "QCBMoptexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=True, include_compile_time=False)


"""
@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_nogf_inc(benchmark, nqubits):
    benchmark.group = "QCBMinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=False, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_nogf_exc(benchmark, nqubits):
    benchmark.group = "QCBMexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=False, include_compile_time=False)
