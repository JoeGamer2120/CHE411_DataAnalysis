import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def main():
    FIC, FIT = getdata("../data/AREA400-2025-04-30_FIC-400C_Obj1_AllRep.csv")
    # vec = flow_percent(FIT)
    # print(vec)
    makeplot(FIC, FIT)
    # avg_flow(FIC, FIT)


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


def avg_flow(FIC, FIT):

    FIT = FIT.reshape(-1, 1)
    FIT = FIT[:, 0]

    if (len(set(FIC[0])) == 1) is False:
        FIC = FIC[0]
    else:
        FIC = FIC[1]

    data = np.column_stack((FIC, FIT))
    index = np.argsort(data, axis=0)
    data_sort = np.take_along_axis(data, index, axis=0)
    data = data_sort.transpose()

    for i in range(len(data[0])):
        check = data[0, i]

    # for i in range(len(data[:,0])):

    return


def makeplot(FIC, FIT):
    """
    Using the data from the passed in csv, plot a chart of the of the flow percent
    against the stem opening for each valve
    """
    p_flow = flow_percent(FIT)
    FICB = FIC[0]
    FICC = FIC[1]
    fig, ax1 = plt.subplots()

    if (len(set(FICB)) == 1) is False:
        ax1.scatter(FICB, p_flow)
        print("FICB")
    elif (len(set(FICC)) == 1) is False:
        ax1.scatter(FICC, p_flow)
        print("FICC")

    ax1.set_xlabel("Stem Opening (%)")
    ax1.set_ylabel("Flow %")
    ax1.set_xlim(-5, 110)
    ax1.set_ylim(-5, 110)


if __name__ == "__main__":
    main()
    plt.show()
