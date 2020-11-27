import numpy as np
import qxelarator
import pytest

import mkl
mkl.set_num_threads(1)

nqubits_list = range(4, 26)
qx = qxelarator.QX()


def first_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit += f"    rx q[{k}], {np.random.rand()}\n"
        circuit += f"    rz q[{k}], {np.random.rand()}\n"
    return circuit


def mid_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit += f"    rz q[{k}], {np.random.rand()}\n"
        circuit += f"    rx q[{k}], {np.random.rand()}\n"
        circuit += f"    rz q[{k}], {np.random.rand()}\n"
    return circuit


def last_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit += f"    rz q[{k}], {np.random.rand()}\n"
        circuit += f"    rx q[{k}], {np.random.rand()}\n"
    return circuit


def entangler(circuit, nqubits, pairs):
    for a, b in pairs:
        circuit += f"    cnot q[{a}], q[{b}]\n"
    return circuit


def build_circuit(nqubits, depth, pairs):
    circuit = f"version 1.0\n\nqubits {nqubits}\n\n.init\n"
    for k in range(nqubits):
        circuit += f"    prep_z q[{k}]\n"
    circuit = first_rotation(circuit, nqubits)
    circuit = entangler(circuit, nqubits, pairs)
    for k in range(depth):
        circuit = mid_rotation(circuit, nqubits)
        circuit = entangler(circuit, nqubits, pairs)

    circuit = last_rotation(circuit, nqubits)
    return circuit


def func(qx):
    qx.execute()


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = build_circuit(nqubits, 9, pairs)
    fname = f"_qc{nqubits}.qasm"
    fout = open(fname, "w")
    fout.write(circuit)
    fout.close()
    qx.set(fname)
    benchmark(func, qx)
