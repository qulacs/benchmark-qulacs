import numpy as np
from intelqs_py import QubitRegister
import pytest

import mkl
mkl.set_num_threads(1)

nqubits_list = range(4, 26)


def first_rotation(state, nqubits):
    for k in range(nqubits):
        state.ApplyRotationX(k, np.random.rand())
        state.ApplyRotationZ(k, np.random.rand())


def mid_rotation(state, nqubits):
    for k in range(nqubits):
        state.ApplyRotationZ(k, np.random.rand())
        state.ApplyRotationX(k, np.random.rand())
        state.ApplyRotationZ(k, np.random.rand())


def last_rotation(state, nqubits):
    for k in range(nqubits):
        state.ApplyRotationZ(k, np.random.rand())
        state.ApplyRotationX(k, np.random.rand())


def entangler(state, nqubits, pairs):
    for a, b in pairs:
        state.ApplyCPauliX(a, b)


def apply_gate(nqubits, depth, pairs, state):
    first_rotation(state, nqubits)
    entangler(state, nqubits, pairs)
    for k in range(depth):
        mid_rotation(state, nqubits)
        entangler(state, nqubits, pairs)

    last_rotation(state, nqubits)


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    state = QubitRegister(nqubits, "base", 0, 0)
    depth = 9
    benchmark(apply_gate, nqubits, depth, pairs, state)
