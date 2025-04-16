### Imported Libraries
import pandas as pd
import numpy as np


def getdata():
    """
    Using the CSV obtained from the UOLab server, this functions grabs the
    data needed to complete this script. Specifically, this grabs the control
    valves position (% open) and flow meter reading.

    Parameters
    ----------
    None.

    Returns
    ----------
    FIC : array
        The values of the control valve % open
    FIT : array
        The value of each flow meter in GPM
    """
    df = pd.read_csv("AREA400-4-9-2025_Test1.csv")
    data = df.to_numpy()

    # NOTE
    # Columns 10, 11, 12, and 13 contain GPM data for each flow meter from FIT-400A, B. C & D
    # Columns 2 & 3 are valve opening position for FIC-400B (note decrepsencies in data) (in order BLOCK1 PID1)
    # Columns 6 & 7 are valve opening position for FIC-400C (in order BLOCK1 PID1)

    # FIC grabs from PID1
    FIC = data[:, [3, 7]]  # In order: B, C
    FIT = data[:, [11, 12, 13, 14]]  # In order: A, B, C, D

    return FIC, FIT


def ReNum(Q, D, nu):
    """
    Obtaines the Reynolds Number using the volumetric flow rate

    Parameters
    ----------
    Q : array
        Volumetric flow rate as provided by FIT-400B
    D : int
        Diameter of Vortex Flow meter
    nu : int
        Kinematic Viscoity of water at given temp

    Returns
    ----------
    Re : array
        Reynold's number with respect to FIT-400C

    """
    return Q * D / nu


if __name__ == "__main__":
    FIC, FIT = getdata()
