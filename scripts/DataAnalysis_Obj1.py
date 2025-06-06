import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
import statsmodels.api as sm

plt.style.use("ggplot")
np.random.seed(7)


def main():
    FIC, FIT, T = getdata("../data/AREA400-2025-04-30_FIC-400C_Obj1_AllRep.csv")
    water = waterdata()
    FIC, FIT, T = sample_flowmeter_data(FIC, FIT, T, 250)
    ResPlot(FIT, 1.049, T, water)
    # Flow_v_Pos(FIC, FIT)
    Flow_v_B(FIT)
    # LinearRegression(FIT)
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

    # FIC grabs from BLOCK1
    FIC = np.transpose(data[:, [2, 6]])  # In order: B, C
    FIT = np.transpose(data[:, [11, 12, 13, 14]])  # In order: A, B, C, D
    T = np.transpose(data[:, [35]])  # Temp data from TE-400A

    return FIC, FIT, T


def waterdata():
    df = pd.read_csv("../data/water.txt", sep="\t", header=0)
    data = df.to_numpy()

    water = np.transpose(data[:, [0, 2, 11]])
    return water


def sample_flowmeter_data(FIC, FIT, T, num_samples):

    FIC = FIC.transpose()
    FIT = FIT.transpose()
    T = T.transpose()

    idx = np.random.choice(len(FIT), size=num_samples, replace=False)
    FIC_sam = FIC[idx, :]
    FIT_sam = FIT[idx, :]
    T_sam = T[idx, :]

    FIC = FIC_sam.transpose()
    FIT = FIT_sam.transpose()
    T = T_sam.transpose()

    return FIC, FIT, T


def ReNum(Q, D, rho, mew):
    """
    Obtains the Reynolds Number wrt FIT-400D (vortex flow meter)
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
    rho :
        Density of water (kg/m^3)
    mew :
        Dynamic Viscocity of Water (Pa*s)

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


def ReNum2(Q, D, T, water):
    """
    Obtains the Reynolds Number wrt FIT-400D (vortex flow meter)
    using the volumetric flow rate as recorded by FIT-400B. The equation
    used is 4 * rho * Q / (pi * D * mew).
    ReNum2 differs from ReNum because it uses density and viscosity
    data from the NIST Webbook data. The data was pulled assuming
    incompressible fluid assumption and that the pressure is 1 atm

    Parameters
    ----------
    Q : array
        Volumetric flow rate (GPM) as provided by FIT-400B
    D : int
        Diameter of Vortex Flow meter (inches)
    T : array
        Temperature readings pulled from TE-400A
    water : array
        Liquid water property data including temp, density and viscosity in SI units
        Pulled from NIST Webbook

    Returns
    ----------
    Re : array
        Reynold's number with respect to FIT-400C
    """

    Re = np.zeros((1, len(Q)))
    Q = Q * (1 / 60) * 0.0037854118  # GPM to m^3/s
    D *= 0.0254  # in to m

    for i in range(len(T[0])):
        index = find_closest(water[0], T[0, i])
        Re[0, i] = np.abs(
            4 * water[1, index] * Q[i] / (np.pi * D * water[2, index])
        )

    return Re


def find_closest(temp, target):
    """
    Find the closest temperature value to the temperature reading
    from TE-400A without overshooting. The change in density and
    viscosity is so small that the fraction of a degree it's off
    is negigable.

    Parameters
    ----------
    temp : array
        List of temperatures from NIST Webbook pulled in smallest increments
        on the NIST Webbook
    target : flt
        Temp value as read by TE-400A
    """
    close = temp[0]
    min_diff = np.abs(target - close)

    for i in range(len(temp)):
        diff = np.abs(target - temp[i])
        if temp[i] > target:
            return i - 1
        elif diff < min_diff:
            min_diff = diff
            close = temp[i]
    return


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


def error_prob_res(FITB, FIT_let, delta_let):

    deltaB = 0.0025
    err = np.zeros_like(FITB)

    for i in range(len(err)):
        err_B = FITB[i] * deltaB
        err_let = FIT_let[i] * delta_let
        err[i] = np.sqrt(err_B**2 + err_let**2)
    return err


def ResPlot(FIT, D, T, water):
    """
    Plots the residual of each flow meter against the Reynolds number
    wrt the vortex meter
    """
    Re = ReNum2(FIT[1], D, T, water)
    Resid = Residual(FIT)

    fig, ax = plt.subplots()

    # ax.scatter(Re, Resid[0], label="Residual of FIT-400A", color="red")
    # ax.scatter(Re, Resid[2], label="Residual of FIT-400C", color="blue")
    ax.scatter(Re, Resid[3], label="Residual of FIT-400D", color="green")

    ax.axline((0, 0), slope=0, color="black")
    # ax.errorbar(Re.transpose(),
    #             Resid[0].transpose(),
    #             capsize=4,
    #             yerr=error_prob_res(FIT[1], FIT[0], 0.0025).transpose(),
    #             fmt='o',
    #             color='red',
    #             label='FIT-400A')

    # ax.errorbar(
    #     Re.transpose(),
    #     Resid[2].transpose(),
    #     capsize=4,
    #     yerr=error_prob_res(FIT[1], FIT[2], 0.0125).transpose(),
    #     fmt="o",
    #     color="blue",
    #     label="FIT-400C",
    # )

    # ax.errorbar(Re.transpose(),
    #             Resid[3].transpose(),
    #             capsize=4,
    #             yerr=error_prob_res(FIT[1], FIT[3], 0.0075).transpose(),
    #             fmt='o',
    #             color='green',
    #             label='FIT-400D')

    ax.set_ylim(-1.5, 1)
    ax.set_xlabel("Reynold's Number wrt to FIT-400C", fontsize=17)
    ax.set_ylabel("Residual (GPM)", fontsize=17)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    # ax.set_xlim(0, max(Re) + 100)
    # ax.set_ylim(min(Resid), max(Resid))
    ax.legend(loc=4)
    # ax.set_title("Resdiual of Flowmeter against FIT-400B")

    fig.savefig("ResidualPlt_FIT-400D_Final.png")

    return


def Flow_v_Pos(FIC, FIT):
    fig, oplot = plt.subplots()

    oplot.scatter(FIC[1], FIT[2], label="FIT-400C", color="blue")
    oplot.scatter(FIC[1], FIT[3], label="FIT-400D", color="green")
    oplot.scatter(FIC[1], FIT[0], label="FIT-400A", color="red")
    oplot.scatter(FIC[1], FIT[1], label="FIT-400B", color="yellow")
    oplot.set_xlabel("Valve Positioning")
    oplot.set_ylabel("Flowrate (GPM)")
    oplot.legend()
    oplot.set_xlim(0, 105)

    return


def Flow_v_B(FIT):
    fig, bplot = plt.subplots()

    # x_err_B = FIT[1] * 0.0025
    # y_err_A = FIT[0] * 0.0025
    # y_err_C = FIT[2] * 0.0125
    # y_err_D = FIT[3] * 0.0075

    # err = np.array([0.0025, 0.0025, 0.0125, 0.0075])

    # bplot.scatter(FIT[1], FIT[0], label="FIT-400A", color="red")
    # bplot.scatter(FIT[1], FIT[2], label="FIT-400C", color="blue")
    bplot.scatter(FIT[1], FIT[3], label="FIT-400D", color="green")

    bplot.axline((0, 0), slope=1, color="black")
    # bplot.axline((0, 0), slope=1 + err[3], color="black")
    # bplot.axline((0, 0), slope=1 - err[3], color="black")

    # bplot.errorbar(FIT[1],
    #                 FIT[0],
    #                 capsize=4,
    #                 xerr=x_err_B,
    #                 yerr=y_err_A,
    #                 fmt='o',
    #                 color='red',
    #                 label='FIT-400A')

    # bplot.errorbar(FIT[1],
    #                 FIT[2],
    #                 capsize=4,
    #                 xerr=x_err_B,
    #                 yerr=y_err_C,
    #                 fmt='o',
    #                 color='blue',
    #                 label='FIT-400C')
    #

    bplot.set_xlabel("Flowrate of FIT-400B (GPM)", fontsize=17)
    bplot.set_ylabel("Flowrate of FIT-400D (GPM)", fontsize=17)
    bplot.set_xlim(0, 10)
    bplot.set_ylim(0, 10)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    # bplot.set_title("Measured Flowrate of Flow Meter vs. Flowrate of FIC-400B")
    bplot.legend()
    fig.savefig("Flow_v_B_Plt_FIT-400D_Final.png")

    return


def LinearRegression(FIT):

    # Reshape required for Library to function correctly
    # Seperation made it a bit easier and should be fairly simple to change
    FITA = FIT[0].reshape(-1, 1)
    FITB = FIT[1].reshape(-1, 1)
    FITC = FIT[2].reshape(-1, 1)
    FITD = FIT[3].reshape(-1, 1)

    # Fit Model
    Y = np.array(
        FITC[:, 0], dtype=float
    )  # Change depending on which model you want to regress

    X = np.array(FITB[:, 0], dtype=float)  # DO NOT CHANGE
    X2 = sm.add_constant(X)  # DO NOT CHANGE

    model = sm.OLS(Y, X2)
    results = model.fit()
    print(results.summary())

    # Initalize Regression Model
    FlowB = linear_model.LinearRegression()

    FlowB.fit(X=FITB, y=FITC)
    #
    print(FlowB.intercept_)
    print(FlowB.coef_)

    return


if __name__ == "__main__":
    main()
    plt.show()
