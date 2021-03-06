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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import re
from scipy.interpolate import interp1d


class Spectra():
    """The Spectra object represents a collection of related spectra
    (spectra vs. concentration, vs. temperature, etc.).

    :param title: Should describe the experiment performed.
    :param ylabel: What does each point represent? Eg. Intensity (a.u)
    :param legend_title: the title that will be used for the plot legends.
    :param label_fun: The function that will be performed to each of the column
                      names. Eg. to convert volume added to concentration.
                      The function must receive a number as parameter and
                      return a number.
     """
    def __init__(self, title=None, ylabel=None, legend_title=None,
                 label_fun=None):
        self.title = title
        self.ylabel = ylabel
        self.legend_title = legend_title
        self.data = None
        self.normdata = None
        self.label_fun = label_fun

    def add_column(self, column, labels: list):
        """Converts to float all fields, eliminating non numeric values.

        :param column:
        :param labels:
        :returns: pandas.DataFrame: Sanitized column

        """
        column = column.apply(pd.to_numeric, errors='coerce')
        column.dropna(inplace=True)
        column.index = pd.to_numeric(column.index)
        column.columns = labels
        self.data = pd.concat((self.data, column), axis=1)

    def add_spectrum(self, filename, labels, **kwargs):
        # if type(filename) is str:
        #    self.name = filename.replace(".csv",
        #                                 "").replace(".xlsx",
        #                                             "").replace(".xls", "")
	# self.data = pd.read_csv(filename, **kwargs)
        # self.sanitize_data()
        self.add_column(pd.read_csv(filename, **kwargs), labels)

    def sanitize_data(self):
        self.sanitize_columns()
        self.sanitize_index()
        self.data.replace(to_replace=",", value=".", regex=True, inplace=True)
        self.data = self.data.apply(pd.to_numeric)
        self.data.dropna(how='all', inplace=True)
        self.data.dropna(how='all', axis=1, inplace=True)

    def sanitize_columns(self):
        newcols = []
        for col in self.data.columns:
            if type(col) is str and "," in col:
                col = col.replace(",", ".")
            newcols.append(float(col))
        self.data.columns = newcols

    def sanitize_index(self):
        newidx = []
        for idx in self.data.index:
            if type(idx) is str and "," in idx:
                idx = idx.replace(",", ".")
            newidx.append(float(idx))
        self.data.index = newidx

    def load_csv_data(self, wavelength: int, basedir=None, start=0.,
                      regex=None, encoding='iso-8859-1'):
        """Reads a series of fluorescence spectra from CSV files
        (Exported from Cary Eclipse, for now.)
        Naming convention: The files should be named as follows:
        "Value Wavelength.csv"
        where "Value" is the variable that is being changed (ie. concentration)
        and "Wavelength" is the emission/excitation wavelength.

        :param wavelength: The wavelength of excitation/emission
        :param should: be specified in the filename
        :param basedir: The path to where the files are located
                        (Default value = None)
        :param start: Which data should be dropped from importing
                      (Default value = 0.)
        :param regex: Regular expression used to extract concentration
                      (Default value = None)
        :param encoding: the encoding of the csv data file to load.
                         (Default value = 'iso-8859-1')
        """

        self.data = pd.DataFrame()
        regex = regex
        if regex is None:
            i = 0
        for file in glob(f"{basedir}*{wavelength}.csv"):
            if regex is not None:
                conc = re.findall(regex, file)[0]
                if self.label_fun is None:
                    conc = float(conc)
                    conc = round(conc*22 / (2000+conc), 2)
                else:
                    conc = self.label_fun(conc)

                if type(conc) in (float, int) and conc <= start:
                    continue
            else:
                i = i + 1
                conc = i

            self.add_spectrum(file, labels = [conc], encoding=encoding, index_col=0, header=1, usecols=[0,1])
            # col = Spectra.sanitize_column(pd.read_csv(file,
            #                                          encoding=encoding,
            #                                          index_col=0, header=1,
            #                                          usecols=[0, 1]), [conc])
            # self.data = pd.concat((self.data, col), axis=1)

        self.data.sort_index(axis=1, inplace=True)

    @staticmethod
    def nearest(array, number):
        """Finds the position of the nearest number in array.

        :param array:
        :param number:

        """
        array = np.asarray(array)
        return array[np.abs(array-number).argmin()]

    def nearest_column(self, number):
        """Returns the column which is nearest to the specified number.

        :param number:

        """
        return Spectra.nearest(self.data.columns, number)

    def nearest_wavelength(self, wavelength):
        """Returns the wavelength which is nearest to the specified number.

        :param wavelength:

        """
        return Spectra.nearest(self.data.index, wavelength)

    def plot_fixed_wavelength(self, wavelength, style=None):
        """Plots the specified wavelength (nearest value).

        :param wavelength:
        :param style:  (Default value = None)

        """
        fixed_wavelength = self.data.loc[self.nearest_wavelength(wavelength)]
        fixed_wavelength.plot(style=style)
        legend_title = self.legend_title
        self.legend_title = "Wavelength (nm)"
        self.decorate_plot(style)
        self.legend_title = legend_title

    def plot_fixed_column(self, number, style=None):
        """Plots the specified column (nearest value).

        :param number:
        :param style:  (Default value = None)

        """
        fixed_col = self.data[self.nearest_column(number)]
        fixed_col.plot(style=style)
        self.decorate_plot(style)

    def plot(self, style=None):
        """Plots the data.

        :param style:  (Default value = None)

        """
        self.data.plot(style=style)
        self.decorate_plot(style)

    def decorate_plot(self, ylabel=None):
        """Sets plot title, ylabel and legend title.

        :param ylabel: if specified, changes the ylabel of the plot.
                       (Default value = None)

        """
        plt.legend(title=self.legend_title, frameon='none', edgecolor='none')
        plt.title(self.title)
        if ylabel is None:
            ylabel = self.ylabel
        plt.ylabel(ylabel)

    def normalize_data(self, fun=lambda x: x/max(x)):
        """Normalizes the data applying the specified lambda."""
        self.normdata = self.data.apply(fun)

    def plot_normalized(self, style=None):
        """Plots the normalized data. If not normalized, it will aplly the
        default normalization to the data.

        :param style: the style to use for the plot lines.
                      (Default value = None)

        """
        if self.normdata is None:
            self.normalize_data()

        self.normdata.plot(style=style)
        self.decorate_plot(ylabel="Norm. intensity (a.u.)")
        plt.ylim([0, 1])

    def plot_maxima(self, style=None):
        """Plots the maximum wavelength vs. column.

        :param style: the style to use for the plot lines.
                      (Default value = None)

        """
        maxima = self.data.idxmax()
        maxima.plot(style=style)
        self.decorate_plot()

    def substract_blank(self, blank):
        # if not np.array_equal(self.data, blank.data):
        #    interpolate = True
        for i in range(len(self.data.columns)):
            f = interp1d(blank.data.index, blank.data.iloc[:, i], kind='cubic')
            self.data.iloc[:, i] = self.data.iloc[:, i] - f(self.data.index)
            # blank.data.iloc[:, i]
