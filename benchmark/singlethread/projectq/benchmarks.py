#!/usr/bin/env python
import pytest
import numpy as np
from projectq import MainEngine
from projectq import ops
from projectq.ops import *

import mkl
mkl.set_num_threads(1)


def run_bench(benchmark, G, locs, nqubits):
    eng = MainEngine()
    reg = eng.allocate_qureg(nqubits)
    qi = take_locs(reg, locs)
    benchmark(run_gate, eng, G, qi)


def run_gate(eng, G, qi):
    G | qi
    eng.flush()


def take_locs(qureg, locs):
    if isinstance(locs, int):
        return qureg[locs]
    elif isinstance(locs, tuple):
        return tuple(qureg[loc] for loc in locs)
    elif isinstance(locs, slice):
        return qureg[sls]
    elif locs is None:
        return qureg
    else:
        raise


def first_rotation(reg, nqubits):
    for k in range(nqubits):
        Rx(np.random.rand()) | reg[k]
        Rz(np.random.rand()) | reg[k]


def mid_rotation(reg, nqubits):
    for k in range(nqubits):
        Rz(np.random.rand()) | reg[k]
        Rx(np.random.rand()) | reg[k]
        Rz(np.random.rand()) | reg[k]


def last_rotation(reg, nqubits):
    for k in range(nqubits):
        Rz(np.random.rand()) | reg[k]
        Rx(np.random.rand()) | reg[k]


def entangler(reg, pairs):
    for a, b in pairs:
        CNOT | (reg[a], reg[b])


def execute_qcbm(eng, reg, n, depth, pairs):
    first_rotation(reg, n)
    entangler(reg, pairs)
    for k in range(depth - 1):
        mid_rotation(reg, n)
        entangler(reg, pairs)

    last_rotation(reg, n)
    eng.flush()


nqubits_list = range(4, 26)


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm(benchmark, nqubits):
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    benchmark.group = "QCBM"
    eng = MainEngine()
    reg = eng.allocate_qureg(nqubits)
    benchmark(execute_qcbm, eng, reg, nqubits, 9, pairs)
