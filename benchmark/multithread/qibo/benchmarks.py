import tensorflow as tf
tf.config.threading.set_inter_op_parallelism_threads(24)
tf.config.threading.set_intra_op_parallelism_threads(24)

import qibo
qibo.set_precision("double")

import numpy as np
from qibo.models import Circuit
from qibo import gates

import pytest

nqubits_list = range(4,26)

def first_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add(gates.RX(k, np.random.rand()))
        circuit.add(gates.RZ(k, np.random.rand()))

def mid_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add(gates.RZ(k, np.random.rand()))
        circuit.add(gates.RX(k, np.random.rand()))
        circuit.add(gates.RZ(k, np.random.rand()))

def last_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add(gates.RZ(k, np.random.rand()))
        circuit.add(gates.RX(k, np.random.rand()))


def entangler(circuit, nqubits, pairs):
    for a, b in pairs:
        circuit.add(gates.CNOT(a, b))

def build_circuit(nqubits, depth, pairs):
    circuit = Circuit(nqubits)
    first_rotation(circuit, nqubits)
    entangler(circuit, nqubits, pairs)
    for k in range(depth):
        mid_rotation(circuit, nqubits)
        entangler(circuit, nqubits, pairs)

    last_rotation(circuit, nqubits)
    return circuit


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = build_circuit(nqubits, 9, pairs)
    state = np.zeros(2**nqubits, dtype=complex)
    state[0]=1
    benchmark(circuit, state)

# @pytest.mark.parametrize('nqubits', nqubits_list)
# @pytest.mark.parametrize('nqubits', nqubits_list)
# def test_QCBM_CUDA(benchmark, nqubits):
#     benchmark.group = "QCBM (cuda)"
#     pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
#     circuit = build_circuit(nqubits, 9, pairs)
#     st = QuantumStateGpu(nqubits)
#     benchmark(circuit.update_quantum_state, st)
