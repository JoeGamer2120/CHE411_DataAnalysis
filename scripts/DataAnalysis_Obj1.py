### Imported Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    FIC, FIT = getdata("../data/AREA400-4-9-2025_Test1.csv")
    ResPlot(FIT, 1.049, 997.77, 0.00095440)
    Flow_v_Pos(FIC, FIT)
    Flow_v_B(FIT)
    return


def getdata(path):
    """
    Using the CSV obtained from the UOLab server, this functions grabs the
    data needed to complete this script. Specifically, this grabs the control
    valves position (% open) and flow meter reading.

    Parameters
    ----------
    path : str
        The path to the CSV of interest
        The path specified must be from where you run the file

    Returns
    ----------
    FIC : array
        The values of the control valve % open returned as a row vector
    FIT : array
        The value of each flow meter in GPM returned as a row vector
    """
    df = pd.read_csv(path)
    data = df.to_numpy()

    # NOTE
    # Columns 10, 11, 12, and 13 contain GPM data for each flow meter from FIT-400A, B. C & D
    # Columns 2 & 3 are valve opening position for FIC-400B (note decrepsencies in data) (in order BLOCK1 PID1)
    # Columns 6 & 7 are valve opening position for FIC-400C (in order BLOCK1 PID1)

    # FIC grabs from PID1
    FIC = np.transpose(data[:, [3, 7]])  # In order: B, C
    FIT = np.transpose(data[:, [11, 12, 13, 14]])  # In order: A, B, C, D

    return FIC, FIT


def ReNum(Q, D, rho, mew):
    """
    Obtaines the Reynolds Number wrt FIT-400D (vortex flow meter)
    using the volumetric flow rate as recorded by FIT-400B. The equation
    usesed is 4 * rho * Q / (pi * D * mew)

    TODO:
        Need to determine how to determine mew via temp
        May be easier to assume but we have temp data
        Also may be easier to use mew and density (dynamic Viscoity)

    Parameters
    ----------
    Q : array
        Volumetric flow rate (GPM) as provided by FIT-400B
    D : int
        Diameter of Vortex Flow meter (inches)
    Nu : int
        Kinematic Viscoity of water at given temp

    Returns
    ----------
    Re : array
        Reynold's number with respect to FIT-400C

    """
    Q = Q * (1 / 60) * 0.0037854118  # GPM to m^3/s
    D *= 0.0254  # in to m
    # For now I will assume that the temp is 22 C for simplicity, check later
    # Property data from NIST Webbook
    rho = 997.77
    mew = 0.00095440  # Pa*s

    return np.abs(4 * rho * Q / (np.pi * D * mew))


def Residual(FIT):
    """
    Determines the residual of the a specified flow meter
    against the standard flow meter (FIT-400B)

    Parameters
    ----------
    FIT : array
        The volumetric flow rates of each of the flow meters

    Returns
    ----------
    Resid : array
        An array of the residual for each flow meter
    """
    Res = np.zeros_like(FIT)

    for i in range(len(FIT)):
        for j in range(len(FIT[0])):
            Res[i, j] = FIT[i, j] - FIT[1, j]

    return Res


def ResPlot(FIT, D, rho, mew):
    """
    Plots the residual of each flow meter against the Reynolds number
    wrt the vortex meter
    """
    Re = ReNum(FIT[1], D, rho, mew)
    # Re = ReNum(FIT[1], 1.049, 997.77, 0.00095440)
    Resid = Residual(FIT)

    fig, ax = plt.subplots()

    ax.scatter(Re, Resid[0], label="Residual of FIT-400A", color="red")
    ax.scatter(Re, Resid[2], label="Residual of FIT-400C", color="blue")
    ax.scatter(Re, Resid[3], label="Residual of FIT-400D", color="green")
    ax.set_xlabel("Reynold's Number wrt to Vortex meter")
    ax.set_ylabel("Residual (GPM)")
    # ax.set_xlim(0, max(Re) + 100)
    # ax.set_ylim(min(Resid), max(Resid))
    ax.legend()

    return


def Flow_v_Pos(FIC, FIT):
    fig, oplot = plt.subplots()

    oplot.scatter(FIC[1], FIT[0], label="FIT-400A", color="red")
    oplot.scatter(FIC[1], FIT[1], label="FIT-400B", color="yellow")
    oplot.scatter(FIC[1], FIT[2], label="FIT-400C", color="blue")
    oplot.scatter(FIC[1], FIT[3], label="FIT-400D", color="green")
    oplot.set_xlabel("Valve Positioning")
    oplot.set_ylabel("Flowrate (GPM);")
    oplot.legend()
    oplot.set_xlim(0, 105)

    return


def Flow_v_B(FIT):
    fig, bplot = plt.subplots()

    bplot.scatter(FIT[1], FIT[0], label="FIT-400A", color="red")
    bplot.scatter(FIT[1], FIT[1], label="FIT-400A", color="blue")
    bplot.scatter(FIT[1], FIT[2], label="FIT-400A", color="green")

    bplot.set_xlabel("Flowrate of FIT-400B (GPM)")
    bplot.set_ylabel("Flowrate (GPM)")
    bplot.legend()

    return


if __name__ == "__main__":
    main()
    plt.show()
