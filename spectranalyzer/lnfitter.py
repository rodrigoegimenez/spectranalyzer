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

from lmfit import minimize, Parameters
import numpy as np
import matplotlib.pyplot as plt
from .lnfun import LNFun
from .multiln import MultiLN


class LNFitter():
    def __init__(self, data, numln=0, fittype=None):
        self.params = Parameters()
        self.paramkeys = []
        self.multiln = MultiLN()
        self.data = data
        self.jsondata = None
        self.fittype = fittype
        for _ in range(numln):
            self.multiln.add_LN(LNFun())

    def extract_params_by_name(self, name):
        params = Parameters()
        for param in self.params.valuesdict():
            if f"{name}y0" == param:
                pname = 'y0'
            elif f"{name}vm" == param:
                pname = 'vm'
            elif f"{name}vmin" == param:
                pname = 'vmin'
            elif f"{name}vmax" == param:
                pname = 'vmax'
            else:
                continue

            params.add(pname, value=self.params[param].value,
                       min=self.params[param].min,
                       max=self.params[param].max)
        return params

    def residual(self, params, x, data):
        self.params = params
        for key in self.paramkeys:
            fun = self.multiln.find_by_name(key)
            params = self.extract_params_by_name(fun.name.replace("-", ""))
            fun.params = params

        model = self.multiln.evaluate(x)

        return (data-model)

    def fit(self, plot=False):
        for lnfun in self.multiln.lnfuns:
            params = lnfun.params.valuesdict()
            name = lnfun.name.replace('-', '')
            self.paramkeys.append(name)
            for param in params:
                self.params.add(f"{name}{param}", value=params[param],
                                min=lnfun.params[param].min,
                                max=lnfun.params[param].max,
                                vary=lnfun.params[param].vary)

        x = np.asarray(self.data.index)
        y = np.asarray(self.data)
        self.out = minimize(self.residual, self.params, args=(x, y),
                            nan_policy='omit')
        if plot:
            self.multiln.plot(x)
            self.data.plot(style=':', linewidth=3, label="Data")
            plt.legend()

    def create_json_data(self):
        curve = {
            'x': self.data.index.values.tolist(),
            'y': self.data.values.tolist(),
            'name': str(self.data.name)
        }

        jsondata = [curve,]
        for col in self.multiln.df:
            x = self.multiln.df[col].index.values.tolist()
            y = self.multiln.df[col].values.tolist()
            name = str(self.multiln.df[col].name)
            curve = {
                'x': x,
                'y': y,
                'name': str(name)
            } 
            jsondata.append(curve)
        self.jsondata = jsondata