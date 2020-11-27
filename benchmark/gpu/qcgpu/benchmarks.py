import numpy as np
import qcgpu
from qcgpu import State
from qcgpu.gate import Gate
from scipy.linalg import expm
import pytest

nqubits_list = range(4, 26)
rx = Gate(expm(np.random.rand() * 0.5j * np.array([[0, 1], [1, 0]])))
rz = Gate(expm(np.random.rand() * 0.5j * np.array([[1, 0], [0, -1]])))


def first_rotation(state, nqubits):
    for k in range(nqubits):
        state.apply_gate(rx, k)
        state.apply_gate(rz, k)


def mid_rotation(state, nqubits):
    for k in range(nqubits):
        state.apply_gate(rz, k)
        state.apply_gate(rx, k)
        state.apply_gate(rz, k)


def last_rotation(state, nqubits):
    for k in range(nqubits):
        state.apply_gate(rz, k)
        state.apply_gate(rx, k)


def entangler(state, nqubits, pairs):
    for a, b in pairs:
        state.cx(a, b)


def apply_circuit(nqubits, depth, pairs):
    state = State(nqubits)
    first_rotation(state, nqubits)
    entangler(state, nqubits, pairs)
    for k in range(depth):
        mid_rotation(state, nqubits)
        entangler(state, nqubits, pairs)

    last_rotation(state, nqubits)
    # return circuit


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    benchmark(apply_circuit, nqubits, 9, pairs)
