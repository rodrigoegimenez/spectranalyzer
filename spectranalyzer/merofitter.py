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
from .lnfitter import LNFitter
from .lnfun import LNFun
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
# from .fitter import Fitter
from .spectra import Spectra


class MeroFitter(Spectra):
    def __init__(self, title=None, ylabel=None, legend_title=None,
                 label_fun=None, xlabel=None):
        super().__init__(title, ylabel, legend_title, label_fun)
        self.name = title
        self.fits = []
        self.xlabel = xlabel

    def create_column_report(self, fitter, colname):
        x = np.asarray(self.data.index)
        areas = []
        vms = []
        y0s = []
        for fun in fitter.multiln.lnfuns:
            vms.append(fun.params["vm"].value)
            y0s.append(fun.params["y0"].value)
            areas.append(fun.calculate_area(x))
        areas = np.asarray(areas)
        totarea = areas.sum()
        areas = areas / totarea * 100
        equil = areas[1]/(areas[0])**2
        data = np.append(areas, [vms, y0s])
        data = np.append(data, [equil])
        index = ["MonomerWater", "DimerWater",
                 "VmMonomer", "VmDimer",
                 "y0Monomer", "y0Dimer",
                 "Equil"]
        return pd.Series(data=data, index=index, name=colname)

    def get_components(self, y0max, kind="Water", vary=False):
        param_mono = Parameters()
        param_dim = Parameters()
        if kind == "Water":
            param_mono.add('y0', value=y0max/2., min=0., max=y0max)
            param_mono.add('vm', value=573, max=600, vary=vary)
            param_mono.add('vmin', value=554, vary=vary)
            param_mono.add('vmax', value=594, vary=vary)
            param_dim.add('y0', value=y0max/2., min=0., max=y0max)
            param_dim.add('vm', value=612, min=580,
                          max=625, vary=vary)
            param_dim.add('vmin', value=594, vary=vary)
            param_dim.add('vmax', value=640, vary=vary)
        elif kind == "Phase":
            param_mono.add('y0', value=y0max/2., min=0., max=y0max)
            param_mono.add('vm', value=580, max=600, vary=vary)
            param_mono.add('vmin', value=554, vary=vary)
            param_mono.add('vmax', value=594, vary=vary)
            param_dim.add('y0', value=y0max/2., min=0., max=y0max)
            param_dim.add('vm', value=620, min=580,
                          max=625, vary=vary)
            param_dim.add('vmin', value=594, vary=vary)
            param_dim.add('vmax', value=650, vary=vary)

        monomero = LNFun(param_mono)
        monomero.name = f"Monomer{kind}"
        dimero = LNFun(param_dim)
        dimero.name = f"Dimer{kind}"

        return monomero, dimero

    def fit_column(self, col, plot=False, interphase=False):
        fitter = LNFitter(self.data[col], fittype="Mero")

        # Maximum cannot be more than, well, the maximum value.
        y0max = fitter.data.max().max()

        lnagua_monomero, lnagua_dimero = self.get_components(y0max,
                                                             kind="Water")
        fitter.multiln.add_LN(lnagua_monomero)
        fitter.multiln.add_LN(lnagua_dimero)

        if interphase:
            lnphase_monomero, lnphase_dimero = self.get_components(
                                               y0max, kind="Phase", vary=True)
            fitter.multiln.add_LN(lnphase_monomero)
            fitter.multiln.add_LN(lnphase_dimero)

        fitter.fit(plot=plot)
        if plot:
            plt.title(f"{self.name} {col}")
            plt.show()

        ser = self.create_column_report(fitter, col)
        self.report = pd.concat([self.report, ser], axis=1, sort=False)
        self.fits.append(fitter)

    def fit_all_columns(self, plot=False, export=False, write_images=False,
                        interphase=False):
        self.report = pd.DataFrame()

        for col in self.data.columns:
            self.fit_column(col, plot, interphase)

        self.report = self.report.transpose()

        if export:
            self.export_fits(write_images)
            self.write_report(plot, write_images)

    def export_fits(self, write_images=False):
        try:
            os.mkdir(self.name)
        except FileExistsError:
            pass

        for fit in self.fits:
            fit.multiln.create_dataframe(np.asarray(self.data.index))
            data = pd.concat([fit.multiln.df, fit.data], axis=1)
            data.to_csv(f"{self.name}{os.path.sep}{fit.data.name}.csv")
            data.plot()
            plt.xlabel("Wavelength (nm)")
            plt.ylabel("Intensity (a.u.)")
            plt.savefig(f"{self.name}{os.path.sep}{fit.data.name}.png")
            plt.close()

    def write_report(self, plot=False, write_images=False):
        try:
            os.mkdir(self.name)
        except FileExistsError:
            pass

        self.report.to_csv(f"{self.name}{os.path.sep}{self.name}-report.csv")
        if write_images:
            self.write_report_graphic(["MonomerWater", "DimerWater"],
                                      "Rel. Area (%)", "RelArea")
            self.write_report_graphic(["VmMonomer", "VmDimer"],
                                      "Wavelength (nm)", "Vms")
            self.write_report_graphic(["y0Monomer", "y0Dimer"],
                                      "Max Intensity (a.u)", "y0s")
            self.write_report_graphic(["Equil"], "Equil (a.u.)",
                                      "Equil")

            if not plot:
                plt.close('all')

    def write_report_graphic(self, columns, ylabel, name):
        self.report[columns].plot(style='-o')
        plt.ylabel(ylabel)
        plt.xlabel(self.xlabel)
        if "Equil" in ylabel:
            plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
        plt.savefig(f"{self.name}{os.path.sep}{self.name}-{name}.png")
