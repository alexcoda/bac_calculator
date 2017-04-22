import pandas as pd
import numpy as np
import itertools
import pickle
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Needed for 3d projection


def main():
    """Adapted from code at: https://tinyurl.com/kdg3oro"""
    bac_table = pd.read_csv("BAC_by_drink.csv", index_col="Body Weight")
    standard_drinks = bac_table.columns.values.astype(float)
    weight = bac_table.index.values.astype(float)
    # standard drinks
    x = np.array([standard_drinks for i in range(len(weight))]).flatten()
    # body weight
    y = np.repeat(weight, len(standard_drinks))
    # bac values
    z = bac_table.values.flatten()
    # colors
    ballmer_points = np.isclose(z, 0.12, rtol=0, atol=0.0051)
    color = ['firebrick' if ballmer else 'royalblue'
             for ballmer in ballmer_points]

    # Do a polyfit
    f = polyfit2d(x, y, z)
    pickle.dump(f, open('bac_polyfit.pkl', 'w'))
    z_fit = polyval2d(x, y, f)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # ax.scatter(x, y, z, c=color)
    ax.scatter(x, y, z_fit, c=color)
    ax.set_xlabel('Standard Drinks')
    ax.set_ylabel('Weight (lbs)')
    ax.set_zlabel('BAC Increase')
    plt.show()


def fit_bac_increase_curve(save=True):
    """Fit a 2d polynomial surface to the bac increase table data."""
    bac_table = pd.read_csv("BAC_by_drink.csv", index_col="Body Weight")
    standard_drinks = bac_table.columns.values.astype(float)
    weight = bac_table.index.values.astype(float)

    x = np.array([standard_drinks for i in range(len(weight))]).flatten()
    y = np.repeat(weight, len(standard_drinks))
    z = bac_table.values.flatten()

    f = polyfit2d(x, y, z)

    if save:
        pickle.dump(f, open('bac_polyfit.pkl', 'w'))
    return f


def polyfit2d(x, y, z, order=3):
    ncols = (order + 1)**2
    G = np.zeros((x.size, ncols))
    ij = itertools.product(range(order+1), range(order+1))
    for k, (i, j) in enumerate(ij):
        G[:, k] = x**i * y**j
    m, _, _, _ = np.linalg.lstsq(G, z)
    return m


def polyval2d(x, y, m):
    order = int(np.sqrt(len(m))) - 1
    ij = itertools.product(range(order+1), range(order+1))
    z = np.zeros_like(x)
    for a, (i, j) in zip(m, ij):
        z += a * x**i * y**j
    return z


if __name__ == "__main__":
    main()
