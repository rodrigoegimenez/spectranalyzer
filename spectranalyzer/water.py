# This file is part of SpectrAnalyzer.
#
# SpectrAnalyzer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SpectrAnalyzer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SpectrAnalyzer.  If not, see <https://www.gnu.org/licenses/>.

from lmfit import Parameters
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import quad
from scipy import interpolate
import os

exp = np.exp
log = np.log


class WaterLN():
    def __init__(self, params=None):
        path = os.path.dirname(os.path.realpath(__file__))
        self.data = pd.read_csv(f"{path}{os.path.sep}normagua.csv",
                                index_col=0)
        self.params = Parameters()
        self.params.add("y0", 1, min=0)
        self.params.add("vm", 1, vary=False)
        self.name = "Water"

    def evaluate(self, x):
        y0 = self.params["y0"].value
        f = interpolate.interp1d(self.data.index, self.data.iloc[:, 0] * y0,
                                 fill_value='extrapolate')
        self.y = f(x)
        return self.y

    def plot(self, x):
        y = self.evaluate(x)
        plt.plot(x, y)

    def plotnorm(self, x):
        y = self.evaluate(x)
        y = y/y.max()
        plt.plot(x, y)

    def calculate_area(self, x):
        area = quad(self.evaluate, x.min(), x.max(), args=())[0]
        return area
