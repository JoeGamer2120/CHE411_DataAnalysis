import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    FIC, FIT = getdata("../data/AREA400-2025-04-30_FIC-400B_Obj2_Rep1.csv")
    # vec = flow_percent(FIT)
    # print(vec)
    makeplot(FIC, FIT)


def getdata(path):
    """
    Uses the CSV from the Rose Hulman Unit Operations historian and pull
    relevant data in order to create characteristic curve. The CSV is
    originally in column vector form so this functions transposes those to be
    row vectors for ease of use. Do not use the outputs as they would be
    displayed in excel

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
    # Notes
    # Columns 2 & 3 are valve opening position for FIC-400B (note decrepsencies in data) (in order BLOCK1 PID1)
    # Columns 6 & 7 are valve opening position for FIC-400C (in order BLOCK1 PID1)

    # FIC grabs from BLOCK1
    FIC = np.transpose(data[:, [2, 6]])  # In order: B, C
    FIT = np.transpose(data[:, [12]])

    return FIC, FIT


def flow_percent(FIT):
    max = np.max(FIT)

    p_flow = (FIT / max) * 100
    return p_flow


def makeplot(FIC, FIT):
    """
    Using the data from the passed in csv, plot a chart of the of the flow percent
    against the stem opening for each valve
    """
    p_flow = flow_percent(FIT)
    fig, ax1 = plt.subplots()

    print(FIC[0])
    print()
    print(p_flow)

    ax1.scatter(FIC[0], p_flow)
    ax1.set_xlabel("Stem Opening (%)")
    ax1.set_ylabel("Flow %")


if __name__ == "__main__":
    main()
    plt.show()
