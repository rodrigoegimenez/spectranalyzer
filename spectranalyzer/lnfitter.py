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
        self.fittype = fittype
        for i in range(numln):
            fun = LNFun()

            y0max = self.data.max()
            # /numln, vary=True, min=self.data.max()/4, max=self.data.max())
            # vm = 0 # self.data.index.min() + (self.data.index.max()
            # - self.data.index.min()) / (numln+1) * (i+1)
            if i == 0:
                fun.set_param('y0', value=y0max/2., min=0., max=y0max)
                fun.set_param('vm', value=416)  # , min=10**7/21300)
                vmin, vmax = fun.get_vmax_vmin(416)
                fun.set_param('vmin', value=vmin)
                fun.set_param('vmax', value=vmax)
            else:
                fun.set_param('y0', value=y0max/2., min=0., max=y0max)
                fun.set_param('vm', value=500)  # , max=10**7/22300,
                vmin, vmax = fun.get_vmax_vmin(500)
                fun.set_param('vmin', value=vmin)
                fun.set_param('vmax', value=vmax)
            # fun.set_param("vm", vm, vary=True)
            # fun.set_param("vmin", vm - 10)
            # fun.set_param("vmax", vm + 20)
            fun.name = f"Component-{i}"
            self.multiln.add_LN(fun)

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
            self.plot()

    def plot(self):
        x = np.asarray(self.data.index)
        self.multiln.plot(x)
        self.data.plot(style=':', linewidth=3, label="Data")
        plt.legend()
