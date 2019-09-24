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
from scipy.integrate import quad

exp = np.exp
log = np.log


class LNFun():
    def __init__(self, params=None):
        self.p = None
        self.a = None
        if params is None:
            self.params = Parameters()
        else:
            self.params = params

    def set_param_vm(self, y0, vm):
        vmax, vmin = self.get_vmax_vmin(vm)
        self.set_param_minmax(y0, vm, vmin, vmax)

    def set_param_minmax(self, y0, vm, vmin, vmax):
        self.params.add("y0", y0)
        self.params.add("vm", vm)
        self.params.add("vmin", vmin)
        self.params.add("vmax", vmax)

    def set_param_pa(self, y0, vm, p, a):
        self.params.add("y0", y0)
        self.params.add("vm", vm)
        self.p = p
        self.a = a

    def get_vmax_vmin(self, vm):
        vm = 10**7/vm
        if (vm <= 22300):
            vmin = -958.4 + .966*vm
            vmax = 1688.8 + 0.986*vm
        else:
            vmin = 1150.7 + 0.877*vm
            vmax = -99.3 + 1.058*vm
        return 10**7/vmax, 10**7/vmin

    def set_param(self, param, value, vary=True, min=-np.inf, max=+np.inf):
        if param not in self.params:
            self.params.add(param, value)
        else:
            self.params[param].value = value
        self.params[param].vary = vary
        self.params[param].min = min
        self.params[param].max = max

    def getpa(self):
        try:
            vmax, vmin = self.params['vmin'].value, self.params['vmax'].value
        except KeyError:
            vmax, vmin = self.get_vmax_vmin(self.params['vm'])
        vm = self.params['vm'].value
        p = (10**7/vm-10**7/vmin)/(10**7/vmax-10**7/vm)
        a = 10**7/vm + ((10**7/vmax-10**7/vmin)*p)/(p**2-1)
        return p, a

    def lognpa(self, x, p, a):
        y0 = self.params['y0'].value
        vm = self.params['vm'].value
        y = y0*exp(-log(2)/(log(p))**2*(log((a-10**7/x)/(a-10**7/vm)))**2)
        if type(y) is np.ndarray:
            y[np.isnan(y)] = 0
        elif np.isnan(y):
            y = 0
        return y

    def evaluate(self, x):
        if (not self.p and not self.a):
            p, a = self.getpa()
        else:
            p, a = self.p, self.a
        y = self.lognpa(x, p, a)
        self.y = y
        return y

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
