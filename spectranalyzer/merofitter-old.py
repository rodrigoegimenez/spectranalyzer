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
from .helpers import fit2ln, logn
import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate

class MeroFitter():
    def __init__(self, spectrum, guessall=True, params=None, iterations=1000, sigma=1E-4):
    # add with tuples: (NAME VALUE VARY MIN  MAX  EXPR  BRUTE_STEP)        
        if guessall:
            self.params = Parameters()
            self.params.add_many(('y0a', spectrum.max(), False, 0.),
                            ('vma', 577., False, 550),
                            ('vmaxa', 607, False),
                            ('vmina', 555, False))#, True, 0., 500))
            self.params.add_many(('y0b', .3, True, 0.),
                            ('vmb', 630, True),
                            ('vmaxb', 670, True),
                            ('vminb', 555, True, 500))#, True, 0.))
        else:
            self.params = params
            self.params['vma'].vary = False
            self.params['vmaxa'].vary = False
            self.params['vmina'].vary = False
            self.params['vmb'].vary = False
            self.params['vmaxb'].vary = False
            self.params['vminb'].vary = False
            self.params['y0a'].vary = True
            self.params['y0b'].vary = True
        self.spectrum = spectrum
        self.iterations = iterations
        self.sigma = sigma
        self.guessall = guessall


    @staticmethod
    def invertParam(param):
        param.vary = not param.vary
    
    def invertParams(self):
        for param in self.params:
            MeroFitter.invertParam(self.params[param])
    
    def iterativeFit(self):
        if self.guessall:
            self.invertParams()
        else:#delete this part
            self.invertParams()
        out = fit2ln(self.spectrum, self.params)
        #print(sum(abs(out.residual)))
        #print(out.params.pretty_print())
        return out, sum(abs(out.residual))

    @staticmethod
    def plotDeconvolution(spectrum, params, which="all"):
        #params = minimizeoutput.params
        y0a = params['y0a']
        vma = params['vma']
        y0b = params['y0b']
        vmb = params['vmb']
        vmaxa = params['vmaxa']
        vmaxb = params['vmaxb']
        vmina = params['vmina']
        vminb = params['vminb']
        x = np.asarray(spectrum.index)
        y1 = logn(x, y0a, vma, vmaxa, vmina)
        y2 = logn(x, y0b, vmb, vmaxb, vminb)
        if which == "all":
            spectrum.plot(style='o', label="Original data")
        if which == "all" or which == "Monomer":
            plt.plot(x, y1, label="Water monomer")
        if which == "all" or which == "Dimer":
            plt.plot(x, y2, label="Water dimer")
        if which == "all":
            plt.plot(x, y1+y2, label="Sum")
        
        plt.legend()
        if which == "all":
            plt.show()
    
    @staticmethod
    def filterParams(params):
        fittedparams = {}
        fittedstderrs = {}
        for param in params:
            if params[param].stderr != 0:
                fittedparams[param] = params[param].value
                fittedstderrs[param] = params[param].stderr
        return fittedparams, fittedstderrs

    @staticmethod
    def getParams(out, lastout):
        fittedparams, fittedstderrs = MeroFitter.filterParams(out.params)
        fittedparams2, fittedstderrs2 = MeroFitter.filterParams(lastout.params)
        fittedparams.update(fittedparams2)
        fittedstderrs.update(fittedstderrs2)
        return fittedparams, fittedstderrs
    
    def plot(self, which="all"):
        MeroFitter.plotDeconvolution(self.spectrum, self.fittedparams, which)
            
    def fit(self, plot=False, quiet=False):
        out = fit2ln(self.spectrum, self.params)
        lastout = out
        lastres = sum(abs(out.residual))
        res = 0
        reschange = []
        iters = self.iterations
        self.converged = False
        for i in range(iters):
            self.params = out.params
            out, res = self.iterativeFit()#spectrum, out.params)
            #print(abs(res-lastres))
            if abs(res-lastres) < self.sigma:
                print(f"Converged after {i} iterations. Residual: {res}. Change in residuals: {abs(res-lastres):.2E}.")
                self.converged = True
                break
            reschange.append(abs(res-lastres))
            if iters-i > 1:
                lastout = out
            
            lastres = res
                #print(f"i: {i}")
            
            if (i%200 == 0 and not quiet):
                print(f"Fitting... iteration: {i}. Change in residuals {reschange[-1]:.2E}")
                
        if not self.converged:
            print(f"Not converging after {self.iterations} iterations. Last change in residuals: {reschange[self.iterations-1]:.2E}")
            #print(out.params.pretty_print())
            #print(lastout.params.pretty_print())
            #print(len(reschange))

        if plot:
            plt.plot(np.arange(0,len(reschange)), reschange, label="Change in residuals.")
            plt.legend(loc='best')
            plt.xlabel("Iteration (n)")
            plt.ylabel("Absolute change in sum of residuals.")
            plt.ylim(0,.1)
        #print(reschange[-1])
            plt.show()
            MeroFitter.plotDeconvolution(self.spectrum,out.params)

        self.fittedparams, self.fittedstderrs = MeroFitter.getParams(out, lastout)
        #print(self.fittedparams)
        self.residuals = out.residual
    
    def get_name(self):
        try:
            return self.spectrum.name
        except AttributeError as ae:
            print(ae)
            return "AttributeError"
    
    def set_title(self, title):
        self.title = title


    def integrateAreas(self, which="all"):
        #params = minimizeoutput.params
        params = self.fittedparams
        spectrum = self.spectrum
        y0a = params['y0a']
        vma = params['vma']
        y0b = params['y0b']
        vmb = params['vmb']
        vmaxa = params['vmaxa']
        vmaxb = params['vmaxb']
        vmina = params['vmina']
        vminb = params['vminb']
        x = np.asarray(spectrum.index)
        #y1 = logn(x, y0a, vma, vmaxa, vmina)
        #y2 = logn(x, y0b, vmb, vmaxb, vminb)
        #print(x)
        area1 = integrate.quad(logn, x.min(), x.max(),args=(y0a, vma, vmaxa, vmina))
        area2 = integrate.quad(logn, x.min(), x.max(),args=(y0b, vmb, vmaxb, vminb))
        return area1, area2