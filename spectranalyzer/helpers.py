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
exp = np.exp
log = np.log

# La asimetría p y el número de onda límite a quedan definidas por vmin y vmax
def getpa(vm, vmax, vmin):
    vmax, vmin = vmin, vmax
    p = (10**7/vm-10**7/vmin)/(10**7/vmax-10**7/vm)
    a = 10**7/vm + ((10**7/vmax-10**7/vmin)*p)/(p**2-1)
    return p, a

# Función lognormal teniendo todos los parámetros definidos
def lognpa(x,y0,vm,p,a):
    y = y0*exp(-log(2)/(log(p))**2*(log((a-10**7/x)/(a-10**7/vm)))**2) 
    try:
        y[np.isnan(y)] = 0
    except TypeError:
        if np.isnan(y):
            y = 0
#    y[np.isnan(y)] = 0
    return y

# Calcular primero p y a y luego llamar a la función lognormal
def logn(x, y0, vm, vmax, vmin):
    p, a = getpa(vm, vmax, vmin)
    #print(p,a)
    y = lognpa(x, y0, vm, p, a)
    return y


def residual(params, x, data = None):
    y0a = params['y0a']
    vma = params['vma']
    y0b = params['y0b']
    vmb = params['vmb']
    vmaxa = params['vmaxa']
    vmina = params['vmina']
    vmaxb = params['vmaxb']
    vminb = params['vminb']
    
    model = logn(x, y0a, vma, vmaxa, vmina) + logn(x, y0b, vmb, vmaxb, vminb)
    
    if data is None:
        return model
    else:
        return (data-model)

def fit2ln(spectrum, params = None):
    x = np.asarray(spectrum.index)
    y = np.asarray(spectrum)
    if params is None:
        params = Parameters()
        params.add('y0a', value=1., min=0.)
        params.add('vma', value=10**7/580)
        params.add('y0b', value=0.6, min=0.)
        params.add('vmb', value=10**7/620)
        params.add('vmina', value=10**7/560)
        params.add('vmaxa', value=10**7/602)
        params.add('vminb', value=10**7/602)
        params.add('vmaxb', value=10**7/631)
    
    out = minimize(residual, params, args=(x, y), nan_policy='raise')
    #model = residual(params, x)
    #res = residual(params, x, spectrum)
    
    return out

def hillfun(x, imax, Kd, n):
    return imax*x**n / (Kd**n + x**n)

def hillresidual(params, x, data):
    imax = params['imax']
    Kd = params['Kd']
    n = params['n']
    model = hillfun(x, imax, Kd, n)
    return (data-model)

def fithill(data):
    x = np.asarray(data.index)
    y = np.asarray(data)
    params = Parameters()
    params.add('imax', value=10., min=0.)
    params.add('Kd', value=5., min=0.)
    params.add('n', value=1., min=0.)
    return minimize(hillresidual, params, args=(x, y))