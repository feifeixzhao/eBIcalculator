import os
import numpy as np
import matplotlib.pyplot as plt
import scipy
from scipy import stats 
import pandas as pd
import geopandas as gpd
import cartopy.crs as ccrs
from matplotlib.lines import Line2D
from scipy.stats import linregress


def fit_regression(x, y, mode="log-x", return_r2=False):
    """
    Fit a regression with optional log-transforms, and always compute R²
    in the space of the fit when return_r2=True.
    """
    # filter out non-finite / non-positive
    mask = (x > 0) & np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    # dispatch fit
    if mode == "linear":
        m, b = np.polyfit(x, y, 1)
        predict = lambda xx: m*xx + b

    elif mode == "log-y":
        y_log = np.log10(y)
        m, b = np.polyfit(x, y_log, 1)
        predict = lambda xx: 10**(m*xx + b)

    elif mode == "log-x":
        x_log = np.log10(x)
        m, b = np.polyfit(x_log, y, 1, rcond=1e-12)
        predict = lambda xx: m*np.log10(xx) + b

    elif mode == "log-log":
        x_log = np.log10(x)
        y_log = np.log10(y)
        m, b = np.polyfit(x_log, y_log, 1)
        predict = lambda xx: 10**(m*np.log10(xx) + b)

    else:
        raise ValueError("mode must be one of 'linear','log-y','log-x','log-log'")

    # now compute R² in the appropriate space
    r2 = None
    if return_r2:
        if mode in ("linear", "log-x"):
            y_hat = predict(x)
            ss_res = ((y - y_hat)**2).sum()
            ss_tot = ((y - y.mean())**2).sum()
        else:  # log-y or log-log
            y_log = np.log10(y)
            if mode == "log-y":
                yhat_log = m*x + b
            else:  # log-log
                yhat_log = m*np.log10(x) + b
            ss_res = ((y_log - yhat_log)**2).sum()
            ss_tot = ((y_log - y_log.mean())**2).sum()

        r2 = 1 - ss_res/ss_tot

    if return_r2:
        return m, b, predict, r2
    else:
        return m, b, predict






def plot_regression(x, y, predict, ax=None, label="Regression"):
    """
    Plot original data points and the regression line.

    Parameters:
        x (array-like): Original independent variable data.
        y (array-like): Original dependent variable data.
        predict (function): Function that takes x-values and returns predicted y-values (on original scale).
        ax (matplotlib.axes.Axes, optional): An axes object to plot on. Creates one if None.
        label (str): Label for the regression line.

    Returns:
        ax (matplotlib.axes.Axes): The axes object with the plot.
    """
    if ax is None:
        fig, ax = plt.subplots()
    
    # Plot data points.
    ax.scatter(x, y, color='blue', label="Data Points")
    
    # Create a set of x-values for plotting the regression line.
    x_line = np.linspace(np.min(x), np.max(x), 100)
    y_line = predict(x_line)
    ax.plot(x_line, y_line, color='red', label=label)
    
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend()
    return ax


def classify_river(sinuosity, mean_bi):
    if mean_bi >= 3.5:
        return 'B'  # Multichannels
    elif mean_bi >= 1.4:
        if sinuosity >= 1.4:
            return 'HSW'  # High-sinuosity wandering
        else:
            return 'LSW'  # Low-sinuosity wandering
    else:
        return 'M'  # Single channel
    

# Helper function to load discharge data based on the Galeazzi file
def load_discharge_data(river_name):
    discharge_dir = r'C:\Users\Feifei\Box\BR_remote_sensing\water_discharge_data\processed'
    galeazzi_file_path = r"C:\Users\Feifei\Box\BR_remote_sensing\Galeazzi_eBI.csv"
    galeazzi_df = pd.read_csv(galeazzi_file_path)
    discharge_file_name = galeazzi_df.loc[galeazzi_df['River_Station'] == river_name, 'ID_discharge'].values
    if len(discharge_file_name) > 0:
        discharge_file = f"{discharge_file_name[0]}.csv"
        discharge_path = os.path.join(discharge_dir, discharge_file)
        if os.path.exists(discharge_path):
            discharge_df = pd.read_csv(discharge_path)
            discharge_df['date'] = pd.to_datetime(discharge_df['date'], format='%m/%d/%Y')
            discharge_df['Year'] = discharge_df['date'].dt.year
            yearly_avg_discharge = discharge_df.groupby('Year')['Q'].mean().reset_index()
            return yearly_avg_discharge
        else:
            print(f"Discharge file not found for {river_name}: {discharge_file}")
            return pd.DataFrame()
    else:
        print(f"ID_discharge not found for {river_name} in Galeazzi file.")
        return pd.DataFrame()
