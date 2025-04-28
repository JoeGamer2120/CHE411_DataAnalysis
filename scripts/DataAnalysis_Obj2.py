import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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


