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

import numpy as np
import pandas as pd


class MultiLN():
    def __init__(self):
        self.lnfuns = []

    def add_LN(self, lnfun):
        self.lnfuns.append(lnfun)

    def plot(self, x):
        self.create_dataframe(x)
        self.df.plot()

    def find_by_name(self, name):
        for fun in self.lnfuns:
            if fun.name.replace("-", "") == name:
                return fun

    def evaluate(self, x):
        self.create_dataframe(x)
        return np.asarray(self.df["Total"])

    def create_dataframe(self, x):
        self.df = pd.DataFrame(index=x)
        total = np.zeros(x.shape)
        for lnfun in self.lnfuns:
            y = lnfun.evaluate(x)
            total = total + y
            self.df[lnfun.name] = pd.Series(data=y, index=x)
        self.df["Total"] = pd.Series(data=total, index=x)
        return self.df
