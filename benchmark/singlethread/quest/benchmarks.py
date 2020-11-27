import numpy as np
from pyquest_cffi import quest
import pytest

import mkl
mkl.set_num_threads(1)

env = quest.createQuESTEnv()
nqubits_list = range(4, 26)


def first_rotation(qubits, nqubits):
    for k in range(nqubits):
        quest.rotateX(qubits, k, np.random.rand())
        quest.rotateZ(qubits, k, np.random.rand())


def mid_rotation(qubits, nqubits):
    for k in range(nqubits):
        quest.rotateZ(qubits, k, np.random.rand())
        quest.rotateX(qubits, k, np.random.rand())
        quest.rotateZ(qubits, k, np.random.rand())


def last_rotation(qubits, nqubits):
    for k in range(nqubits):
        quest.rotateZ(qubits, k, np.random.rand())
        quest.rotateX(qubits, k, np.random.rand())


def entangler(qubits, nqubits, pairs):
    for a, b in pairs:
        quest.controlledNot(qubits, a, b)


def run_qcbm(qubits, nqubits, depth, pairs):
    first_rotation(qubits, nqubits)
    entangler(qubits, nqubits, pairs)
    for k in range(depth):
        mid_rotation(qubits, nqubits)
        entangler(qubits, nqubits, pairs)

    last_rotation(qubits, nqubits)
    return qubits


def run_bench(benchmark, gate, nqubits, args):
    qubits = quest.createQureg(nqubits, env)
    benchmark(gate, qubits, *args)


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    qubits = quest.createQureg(nqubits, env)
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    benchmark(run_qcbm, qubits, nqubits, 9, pairs)
