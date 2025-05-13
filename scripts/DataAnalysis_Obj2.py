import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.style.use("ggplot")


def main():
    FIC_Close, FIT_Close = getdata(
        "../data/AREA400-2025-04-30_FIC-400C_Obj2_Closing.csv"
    )
    FIC_Open, FIT_Open = getdata(
        "../data/AREA400-2025-04-30_FIC-400C_Obj2_Opening.csv"
    )
    makeplot(
        FIC_Open,
        FIT_Open,
        FIC_Close,
        FIT_Close,
        "FIC-400C_CharacteristicCurve.png",
    )


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


def flow_percent(flow_rates):
    max = np.max(flow_rates)

    p_flow = (flow_rates / max) * 100
    return p_flow


def avg_flowrates(FIC, FIT):

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

    valve_opening = data[0]
    flow_rates = data[1]
    p_flow = flow_percent(flow_rates)

    unique_openings, inverse_indicies = np.unique(
        valve_opening, return_inverse=True
    )
    avg_flow = np.zeros_like(unique_openings, dtype=float)
    std = np.zeros_like(unique_openings, dtype=float)

    for i in range(len(unique_openings)):
        avg_flow[i] = np.mean(p_flow[inverse_indicies == i])
        std[i] = np.std(p_flow[inverse_indicies == i])

    return np.vstack((unique_openings, avg_flow)), std


def makeplot(FIC_Open, FIT_Open, FIC_Close, FIT_Close, filename):
    """
    Using the data from the passed in csv, plot a chart of the of the flow percent
    against the stem opening for each valve
    """
    fig, ax1 = plt.subplots()
    avg_flow_open, std_open = avg_flowrates(FIC_Open, FIT_Open)
    avg_flow_close, std_close = avg_flowrates(FIC_Close, FIT_Close)

    # ax1.scatter(avg_flow[0], p_flow)
    ax1.errorbar(
        avg_flow_open[0],
        avg_flow_open[1],
        capsize=4,
        yerr=std_open,
        fmt="o",
        color="red",
        label="Opening",
    )
    ax1.errorbar(
        avg_flow_close[0],
        avg_flow_close[1],
        capsize=4,
        yerr=std_close,
        fmt="s",
        color="green",
        label="Closing",
    )
    ax1.set_xlabel("Stem Opening (%)", fontsize=17)
    ax1.set_ylabel("Flow %", fontsize=17)
    ax1.set_xlim(-5, 110)
    ax1.set_ylim(-5, 110)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    ax1.legend(loc=2)
    fig.savefig(filename)


if __name__ == "__main__":
    main()
    plt.show()
