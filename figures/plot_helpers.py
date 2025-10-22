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
from scipy.optimize import curve_fit

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
from matplotlib.lines import Line2D
from scipy.stats import linregress


def configure_matplotlib(font_size=20, label_size=None, tick_label_size=None,
                         legend_font_size=None):
    """Set matplotlib's global style parameters."""
    if label_size is None:
        label_size = font_size
    if tick_label_size is None:
        tick_label_size = font_size
    if legend_font_size is None:
        legend_font_size = font_size

    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.labelsize'] = label_size
    plt.rcParams['xtick.labelsize'] = tick_label_size
    plt.rcParams['ytick.labelsize'] = tick_label_size
    plt.rcParams['legend.fontsize'] = legend_font_size


def load_combined_statistics(csv_path):
    """Load the eBI combined statistics CSV."""
    return pd.read_csv(csv_path)


def fit_regression(x, y, mode="log-x", return_r2=False):
    """
    Fit a regression with optional log-transforms, and always compute R²
    in the space of the fit when return_r2=True.

    Modes:
      - "linear"  : y = m*x + b
      - "log-x"   : y = m*log10(x) + b   (semi-log, straight line if x-axis is log)
      - "log-y"   : log10(y) = m*x + b   (semi-log, straight line if y-axis is log)
      - "log-log" : log10(y) = m*log10(x) + b  (power law, straight line if both axes are log)
    """
    # filter out non-finite / non-positive
    mask = (x > 0) & (y > 0) & np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]

    if mode == "linear":
        m, b = np.polyfit(x, y, 1)
        predict = lambda xx: m*xx + b

    elif mode == "log-x":  # semi-log: y vs log10(x)
        x_log = np.log10(x)
        m, b = np.polyfit(x_log, y, 1)
        predict = lambda xx: m*np.log10(xx) + b

    elif mode == "log-y":  # semi-log: log10(y) vs x
        y_log = np.log10(y)
        m, b = np.polyfit(x, y_log, 1)
        predict = lambda xx: 10**(m*xx + b)

    elif mode == "log-log":  # power law
        x_log = np.log10(x)
        y_log = np.log10(y)
        m, b = np.polyfit(x_log, y_log, 1)
        predict = lambda xx: 10**(m*np.log10(xx) + b)

    else:
        raise ValueError("mode must be one of 'linear','log-y','log-x','log-log'")

    # Compute R²
    r2 = None
    if return_r2:
        if mode in ("linear", "log-x"):
            y_hat = predict(x)
            ss_res = ((y - y_hat)**2).sum()
            ss_tot = ((y - y.mean())**2).sum()
        elif mode == "log-y":
            y_log = np.log10(y)
            yhat_log = m*x + b
            ss_res = ((y_log - yhat_log)**2).sum()
            ss_tot = ((y_log - y_log.mean())**2).sum()
        elif mode == "log-log":
            y_log = np.log10(y)
            yhat_log = m*np.log10(x) + b
            ss_res = ((y_log - yhat_log)**2).sum()
            ss_tot = ((y_log - y_log.mean())**2).sum()
        r2 = 1 - ss_res/ss_tot

    return (m, b, predict, r2) if return_r2 else (m, b, predict)




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
    

def fit_bounded_power(x, y, y0=1.0, p0=None, return_r2=False):
    """
    Fit the model y = y0 - A*x^s for x>0, y<y0.
    
    Parameters:
      x      : array-like, independent variable (must be >0)
      y      : array-like, dependent variable (should be < y0)
      y0     : float, the known upper asymptote
      p0     : tuple (A0, s0), initial guesses for A and s. 
               If None, defaults to A0=(y0 - y.min()), s0=0.1.
      return_r2 : bool, if True also return R² in y-space.
    
    Returns:
      if return_r2:
        A, s, predict_func, r2
      else:
        A, s, predict_func
      where predict_func(xx) gives y0 - A*xx**s
    """
    # filter valid data
    x = np.asarray(x)
    y = np.asarray(y)
    mask = (x > 0) & np.isfinite(x) & np.isfinite(y) & (y < y0)
    x, y = x[mask], y[mask]
    if p0 is None:
        A0 = max(1e-6, y0 - np.min(y))
        s0 = 0.1
        p0 = (A0, s0)

    # define model with fixed y0
    def _model(x, A, s):
        return y0 - A * x**s

    popt, pcov = curve_fit(_model, x, y, p0=p0, maxfev=2000)
    A_fit, s_fit = popt

    # build predict function
    predict = lambda xx: y0 - A_fit * np.power(xx, s_fit)

    if return_r2:
        y_hat = predict(x)
        ss_res = np.sum((y - y_hat)**2)
        ss_tot = np.sum((y - y.mean())**2)
        r2 = 1 - ss_res/ss_tot
        return A_fit, s_fit, predict, r2
    else:
        return A_fit, s_fit, predict


def plot_bounded_power(x, y, y0=1.0, ax=None, label=None, **plot_kw):
    """
    Fit y = y0 - A*x^s and plot data + fitted curve.

    Parameters:
      x, y   : array-like data points
      y0     : float, upper asymptote
      ax     : matplotlib Axes (created if None)
      label  : str, label for the fitted curve in legend
      plot_kw: additional kwargs passed to ax.plot for the fit line

    Returns:
      ax, and the (A, s, r2) tuple
    """
    if ax is None:
        fig, ax = plt.subplots()
    # scatter data
    ax.scatter(x, y, color='C0', label='Data')
    # fit
    A, s, predict, r2 = fit_bounded_power(x, y, y0=y0, return_r2=True)
    # curve
    x_line = np.logspace(np.log10(x.min()*0.9), np.log10(x.max()*1.1), 200)
    y_line = predict(x_line)
    lbl = label or f"$y={y0:.1f}-({A:.2g})x^{{{s:.2f}}},\,R^2={r2:.2f}$"
    ax.plot(x_line, y_line, label=lbl, **plot_kw)
    ax.set_xscale('log')
    ax.legend()
    return ax, (A, s, r2)

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
