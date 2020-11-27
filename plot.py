import json
import glob
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

liblist = ["qulacs", "yao", "qiskit", "projectq", "quest", "qibo", "intelqs", "qxsimulator"]
liblegend = ["Qulacs", "Yao", "Qiskit", "ProjectQ", "PyQuEST-cffi", "Qibo", "Intel-QS", "qxelerator"]


def load(folder_name):
    filepaths = []

    for libname in liblist:
        if libname != "yao":
            path = f"./benchmark/{folder_name}/{libname}/.benchmarks/*/*.json"
        else:
            path = f"./benchmark/{folder_name}/{libname}/data/*.json"
        flist = glob.glob(path)
        flist = [fname.replace("\\", "/") for fname in flist]
        # pick latest one
        if libname != "yao":
            flist.sort(key=lambda x: int(x.split("/")[-1].split("_")[0]), reverse=True)
        if len(flist) > 0:
            filepaths.append((libname, flist[0]))

    dat = defaultdict(dict)
    for filepath in filepaths:
        data = json.load(open(filepath[1]))

        def fetch_normal(libname, dat, data):
            items = data["benchmarks"]
            for item in items:
                name = item["group"]
                nqubits = int(item["param"])
                stats = item["stats"]
                if len(name) > 4:
                    key = libname + name[4:]
                else:
                    key = libname
                # print(key)
                dat[key][nqubits] = float(stats["min"])

        def fetch_yao(dat, data):
            # print(data.keys())
            d = data["QCBM"]
            nqubits = d["nqubits"]
            times = d["times"]
            for ind, nq in enumerate(nqubits):
                dat["yao"][nq] = times[ind] / 1e9

        if filepath[0] == "yao":
            fetch_yao(dat, data)
        else:
            fetch_normal(filepath[0], dat, data)

    # import pprint
    # pprint.pprint(dat.keys())
    # pprint.pprint(dat)
    return dat


def plot(dat, save_name):
    cmap = plt.get_cmap("tab10")
    plt.figure(figsize=(12, 6))
    cnt = 0
    for ind, name in enumerate(liblist):
        hit = [dname for dname in dat.keys() if dname.startswith(name)]
        if len(hit) == 0:
            continue
        cid = liblist.index(name)
        lw = 2 if name == "qulacs" else 1

        legend = liblegend[ind]
        ls = "--" if name in ["qulacs", "qiskit"] else "-"

        if name not in ["qulacs", "qiskit"]:
            fil = np.array(list(dat[name].items())).T
            plt.plot(fil[0], fil[1], ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
        elif name in ["qulacs"]:
            fil = np.array(list(dat[name].items())).T
            plt.plot(fil[0], fil[1], ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
            fil = np.array(list(dat[name + "opt"].items())).T
            plt.plot(fil[0], fil[1], ".-", label=legend + " with opt", c=cmap(cid), linestyle="-", linewidth=lw)
            if name + "opt4" in dat:
                fil = np.array(list(dat[name + "opt4"].items())).T
                plt.plot(fil[0], fil[1], ".-", label=legend + " with heavy opt", c=cmap(cid), linestyle="-.", linewidth=lw)
        elif name in ["qiskit"]:
            fil = np.array(list(dat[name + "exc"].items())).T
            plt.plot(fil[0], fil[1], ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
            fil = np.array(list(dat[name + "optexc"].items())).T
            plt.plot(fil[0], fil[1], ".-", label=legend + " with opt", c=cmap(cid), linestyle="-", linewidth=lw)

        cnt += 1

    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("# of qubits", fontsize=16)
    plt.ylabel("Time [sec]", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1.0))
    plt.tight_layout()
    plt.savefig("./image/" + save_name)
    # plt.show()
    plt.clf()


def plot_ratio(dat, save_name):
    fil = np.array(list(dat["qulacs"].items())).T
    base = fil[1]
    cmap = plt.get_cmap("tab10")
    plt.figure(figsize=(12, 6))
    cnt = 0
    for ind, name in enumerate(liblist):
        hit = [dname for dname in dat.keys() if dname.startswith(name)]
        if len(hit) == 0:
            continue
        cid = liblist.index(name)
        lw = 2 if name == "qulacs" else 1

        legend = liblegend[ind]
        ls = "--" if name in ["qulacs", "qiskit"] else "-"

        if name not in ["qulacs", "qiskit"]:
            fil = np.array(list(dat[name].items())).T
            plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
        elif name in ["qulacs"]:
            fil = np.array(list(dat[name].items())).T
            plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
            fil = np.array(list(dat[name + "opt"].items())).T
            plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend + " with opt", c=cmap(cid), linestyle="-", linewidth=lw)
            if name + "opt4" in dat:
                fil = np.array(list(dat[name + "opt4"].items())).T
                plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend + " with heavy opt", c=cmap(cid), linestyle="-.", linewidth=lw)
        elif name in ["qiskit"]:
            fil = np.array(list(dat[name + "exc"].items())).T
            plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend, c=cmap(cid), linestyle=ls, linewidth=lw)
            fil = np.array(list(dat[name + "optexc"].items())).T
            plt.plot(fil[0], np.array(fil[1]) / base, ".-", label=legend + " with opt", c=cmap(cid), linestyle="-", linewidth=lw)

        cnt += 1

    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("# of qubits", fontsize=16)
    plt.ylabel("Time (relative to Qulacs)", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1.0))
    plt.tight_layout()
    plt.savefig("./image/" + save_name)
    # plt.show()
    plt.clf()


if __name__ == "__main__":
    for folder in ["singlethread", "multithread", "gpu"]:
        dat = load(folder)
        plot(dat, f"fig_compare_{folder}.pdf")
        plot_ratio(dat, f"fig_ratio_{folder}.pdf")
        plot(dat, f"fig_compare_{folder}.png")
        plot_ratio(dat, f"fig_ratio_{folder}.png")
