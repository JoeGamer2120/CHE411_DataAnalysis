### Imported Libraries
import pandas as pd
import numpy as np


def data():
    df = pd.read_csv("AREA400-4-9-2025_Test1.csv")
    data = df.to_numpy()

    # NOTE
    # Columns 10, 11, 12, and 13 contain GPM data for each flow meter from FIT-400A, B. C & D
    # Columns 2 & 3 are valve opening position for FIC-400B (note decrepsencies in data) (in order BLOCK1 PID1)
    # Columns 6 & 7 are valve opening position for FIC-400C (in order BLOCK1 PID1)

    # Make these two arrays if possible, for simplicity
    FIC_B = data[:, 3]
    FIC_C = data[:, 7]
    FIT_A = data[:, 11]
    FIT_B = data[:, 12]
    FIT_C = data[:, 13]
    FIT_D = data[:, 14]

    FIT = data[:, [11, 14]]
    print(FIT_A)
    print()
    print(FIT_B)
    print()
    print(FIT_C)
    print()
    print(FIT_D)
    print()
    print(FIT)

    return


if __name__ == "__main__":
    data()
