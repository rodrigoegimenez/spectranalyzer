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
from .water import WaterLN
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
        self.report = pd.DataFrame()

    def create_column_report(self, fitter, colname):
        x = np.asarray(self.data.index)
        data = pd.Series(name=colname)
        totarea = 0
        areas = []
        for fun in fitter.multiln.lnfuns:
            data[f"{fun.name}"] = fun.calculate_area(x)
            areas.append(f"{fun.name}")
            totarea = totarea + data[f"{fun.name}"]
            data[f"Vm{fun.name}"] = fun.params["vm"].value
            data[f"y0{fun.name}"] = fun.params["y0"].value
        for area in areas:
            data[f"{area}norm"] = data[area] / totarea * 100
        data[f"Equil0"] = data[areas[1]]/(data[areas[2]])**2
        return data

    def get_components(self, y0max, kind="Water", vary=True):
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
            param_mono.add('vm', value=585, max=600, vary=True)
            param_mono.add('vmin', value=572, vary=vary)
            param_mono.add('vmax', value=596, vary=vary)
            param_dim.add('y0', value=y0max/2., min=0., max=y0max)
            param_dim.add('vm', value=626, min=580,
                          max=625, vary=True)
            param_dim.add('vmin', value=604, vary=vary)
            param_dim.add('vmax', value=666, vary=vary)

        monomero = LNFun(param_mono)
        monomero.name = f"Monomer{kind}"
        dimero = LNFun(param_dim)
        dimero.name = f"Dimer{kind}"

        return monomero, dimero

    def fit_column(self, col, plot=False, interphase=False):
        fitter = LNFitter(self.data[col], fittype="Mero")

        # Maximum cannot be more than, well, the maximum value.
        y0max = fitter.data.max().max()

        if interphase:
            fitter.multiln.add_LN(WaterLN())
            lnphase_monomero, lnphase_dimero = self.get_components(
                                               y0max, kind="Phase")
            # , vary=True)
            fitter.multiln.add_LN(lnphase_monomero)
            fitter.multiln.add_LN(lnphase_dimero)
        else:
            lnagua_monomero, lnagua_dimero = self.get_components(y0max,
                                                                 kind="Water")
            fitter.multiln.add_LN(lnagua_monomero)
            fitter.multiln.add_LN(lnagua_dimero)

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
            # data.plot()
            fit.plot()
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
            columnsarea = []
            columnsequil = []
            if "MonomerPhase" in self.report.columns:
                columnsarea = ["Water",
                               "MonomerPhase", "DimerPhase"]
                columnsequil = ["Equil0"]
            else:
                columnsarea = ["MonomerWater", "DimerWater"]
                columnsequil = ["Equil0"]

            self.write_report_graphic(columnsarea, "Area (a.u.)", "Area")
            normcols = []
            for col in columnsarea:
                normcols.append(f"{col}norm")
            self.write_report_graphic(normcols, "Rel Area (%)", "RelArea")

            self.write_report_graphic(columnsequil, "Equil (a.u.)", "Equil")

            if not plot:
                plt.close('all')

    def write_report_graphic(self, columns, ylabel, name):
        self.report[columns].plot(style='-o')
        plt.ylabel(ylabel)
        if "Rel" in ylabel:
            plt.ylim(0,100)
        plt.xlabel(self.xlabel)
        plt.legend(loc='best')
        plt.title(f"{self.name}-{name}")
        if "Equil" in ylabel:
            plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
        plt.savefig(f"{self.name}{os.path.sep}{self.name}-{name}.png")
