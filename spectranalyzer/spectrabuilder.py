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

from .cibaalimporter import CibaalImporter
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from .helpers import fit2ln, fithill, hillfun
from .merofitter import MeroFitter
from glob import glob

class SpectraBuilder():
    
    def __init__(self, files, tipo, wavelength):
        self.data = pd.DataFrame()
        self.path = os.path.sep.join(files[0].split(os.path.sep)[:-1])
        for file in files:
            spectrum = CibaalImporter(file, tipo)
            spectrum.data.columns = [spectrum.title]
            self.data = pd.concat([self.data, spectrum.data], axis=1, sort=True)
        # This only works with merocyanine from that specific stock, in that specific cuvette
        # with that specific volume and that specific lipid concentration!
        # Must fix!
        self.sanitizeColumns(lambda x: float("{:.2f}".format(int(x)*22/(90*2000)*1000)))
        self.data.sort_index(axis=1, inplace=True)
        self.data.index = pd.to_numeric(self.data.index)
        self.normalize()
        self.wavelength = wavelength
    
    @staticmethod
    def nearest(array, number):
        return array[np.abs(array-number).argmin()]
    
    def nearestCol(self, number):
        return SpectraBuilder.nearest(self.data.columns, number)
        
    def nearestWavelength(self, wavelength):
        return SpectraBuilder.nearest(self.data.index, wavelength)
    
    def fixedWavelength(self, wavelength):
        return self.data.loc[self.nearestWavelength(wavelength)]
    
    def fixedCol(self, number):
        return self.data[self.nearestCol(number)]
    
    def plot(self, which="Orig", savefig=False):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_position([0.1,0.1,0.75,0.8])
        if which == "Norm":
            ax.set_ylabel("Norm. intensity (a.u.)")
            self.normdata.plot(ax = ax)
        elif which == "Delta":
            ax.set_ylabel("Delta fluorescence (a.u.)")
            self.delta.plot(ax = ax)
        else:
            ax.set_ylabel("Intensity (a.u.)")
            self.data.plot(ax = ax)
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title(f"{self.title}@{self.wavelength}nm")
        if savefig:
            fig.savefig(f"{self.path}{os.path.sep}{self.title}-{self.wavelength}-{which}.png", dpi=150)
        
    def plotMonomerDimer(self, suffix=""):
        self.fixedWavelength(590).plot(label=f"Monomer {suffix}", style='o-')
        self.fixedWavelength(620).plot(label=f"Dimer {suffix}", style='o-')
        plt.legend()
        plt.xlabel(r"[MC]/[Lip] ($10^{-3}$)")
        plt.ylabel(r"Intensity (a.u.)")
        plt.title(self.title)
    
    def plotMonomerDimerRatio(self, suffix=""):
        monomer = self.fixedWavelength(590)
        dimer = self.fixedWavelength(620)
        (monomer/dimer).plot()
        
    def normalize(self):
        self.normdata = self.data/self.data.max()
    
    def sanitizeColumns(self, fun):
        self.data.columns = self.data.columns.map(fun)
    
    def set_title(self, title):
        self.title = title
        
    def fitHillWl(self, wavelength, axis=None):
        """Perform Hill equation fitting. At specified wavelength."""
        data = self.fixedWavelength(wavelength)
        result = fithill(data)
        imax = result.params['imax']
        Kd = result.params['Kd']
        n = result.params['n']
        x = np.linspace(data.index.min(),data.index.max())
        y = hillfun(x, imax.value, Kd.value, n.value)
        plt.plot(x,y)
        data.plot(style='o', label=self.title)
        #plt.show()
        print(f"Fitting {self.title} at Wavelength {wavelength}")
        print(f'Imax: {imax.value} +- {imax.stderr}')
        print(f'Kd: {Kd.value} +- {Kd.stderr}')
        print(f'n: {n.value} +- {n.stderr}')
        return result
    
    def calcularDelta(self, column, normalized=False):
        self.delta = pd.DataFrame()
        #self.delta.index = self.data.index
        for col in self.data.columns:
            if normalized:
                self.delta[col] = self.normdata[col]-self.normdata[column]
            else:
                self.delta[col] = self.data[col]-self.data[column]
    
    def fitLN2(self, quiet=False, plot=False):
        self.fits = []
        for column in self.data.columns[::-1]:
            spectrum = self.data[column]
            guessall = True
            params = None
            if len(self.fits)>0:
                guessall = False
                params = self.fits[-1].params
            fit = MeroFitter(spectrum, iterations=10000, guessall=guessall, params=params)
            if not quiet:
                print(f"Fitting {self.path} {fit.get_name()}...")
            fit.fit(quiet=quiet, plot=plot)
            #fit.set_title(spectra.path)
            self.fits.append(fit)

    @staticmethod
    def importSpectra(basedir, wavelength):
        files = glob(f"{basedir}/*{wavelength}*csv")
        title = files[0].split(os.path.sep)[-2]
        data = SpectraBuilder(files,"Cary", wavelength=wavelength)
        data.set_title(title)
        return data
    
    @staticmethod
    def massiveImporter(data, wavelengths):
        ret = []
        for item in data:
            for wavelength in wavelengths:
                ret.append(SpectraBuilder.importSpectra(item, wavelength))
        return ret