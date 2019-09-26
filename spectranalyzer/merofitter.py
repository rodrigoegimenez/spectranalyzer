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
        index = ["MonomerAgua", "DimerAgua",
                 "VmRelaxed", "VmNonRelaxed",
                 "y0Relaxed", "y0Nonrelaxed",
                 "Equil"]
        return pd.Series(data=data, index=index, name=colname)

    def fit_column(self, col, plot=False):
        fitter = LNFitter(self.data[col], fittype="Mero")

        # Maximum cannot be more than, well, the maximum value.
        y0max = fitter.data.max().max()

        lnagua_monomero = LNFun()
        lnagua_monomero.name = "MonomeroAgua"
        lnagua_dimero = LNFun()
        lnagua_dimero.name = "DimeroAgua"

        lnagua_monomero.set_param('y0', value=y0max/2., min=0., max=y0max)
        lnagua_monomero.set_param('vm', value=573, max=600, vary=False)
        lnagua_monomero.set_param('vmin', value=554, vary=False)
        lnagua_monomero.set_param('vmax', value=594, vary=False)

        lnagua_dimero.set_param('y0', value=y0max/2., min=0., max=y0max)
        lnagua_dimero.set_param('vm', value=612, min=580,
                                max=625, vary=False)
        lnagua_dimero.set_param('vmin', value=594, vary=False)
        lnagua_dimero.set_param('vmax', value=640, vary=False)

        fitter.multiln.add_LN(lnagua_monomero)
        fitter.multiln.add_LN(lnagua_dimero)

        fitter.fit(plot=plot)
        if plot:
            plt.title(f"{self.name} {col}")
            plt.show()

        ser = self.create_column_report(fitter, col)
        self.report = pd.concat([self.report, ser], axis=1, sort=False)
        self.fits.append(fitter)

    def fit_all_columns(self, plot=False, export=False, write_images=False):
        self.report = pd.DataFrame()

        for col in self.data.columns:
            self.fit_column(col, plot)

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
            self.write_report_graphic(["MonomerAgua", "DimerAgua"],
                                      "Rel. Area (%)", "RelArea")
            self.write_report_graphic(["VmRelaxed", "VmNonRelaxed"],
                                      "Wavelength (nm)", "Vms")
            self.write_report_graphic(["y0Relaxed", "y0Nonrelaxed"],
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
