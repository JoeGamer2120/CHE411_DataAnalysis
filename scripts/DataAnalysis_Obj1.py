### Imported Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
        The values of the control valve % open
    FIT : array
        The value of each flow meter in GPM
    """
    df = pd.read_csv(path)
    data = df.to_numpy()

    # NOTE
    # Columns 10, 11, 12, and 13 contain GPM data for each flow meter from FIT-400A, B. C & D
    # Columns 2 & 3 are valve opening position for FIC-400B (note decrepsencies in data) (in order BLOCK1 PID1)
    # Columns 6 & 7 are valve opening position for FIC-400C (in order BLOCK1 PID1)

    # FIC grabs from PID1
    FIC = data[:, [3, 7]]  # In order: B, C
    FIT = data[:, [11, 12, 13, 14]]  # In order: A, B, C, D

    return FIC, FIT


def ReNum(Q, D, Nu):
    """
    Obtaines the Reynolds Number wrt FIT-400D (vortex flow meter)
    using the volumetric flow rate as recorded by FIT-400B

    TODO:
        Need to determine how to determine Nu via temp
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
    # For now I will assume that the temp is 22 C for simplicity, check later

    Q = Q * (1 / 60) * 0.0037854118  # GPM to m^3/s
    D *= 0.0254  # in to m

    return Q * D / Nu


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
        FIT-400B should all be 0
    """
    Res = np.zeros_like(FIT)

    for i in range(len(Res[0])):
        for j in range(len(Res)):
            Res[j, i] = FIT[j, i] - FIT[j, 1]

    return Res


def ResPlot():
    fig, ax = plt.subplot()

    return


if __name__ == "__main__":
    FIC, FIT = getdata("../data/AREA400-4-9-2025_Test1.csv")
    Res = Residual(FIT)
    # print(Res[:, [1]])
