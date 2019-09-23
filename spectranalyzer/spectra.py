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


class Spectra():
    """ """
    def __init__(self, title=None, ylabel=None, legend_title=None):
        self.title = title
        self.ylabel = ylabel
        self.legend_title = legend_title
        self.data = None
        self.normdata = None

    @staticmethod
    def sanitize_columns(data, labels: list):
        """Converts to float all fields, eliminating non numeric values.

        :param data: pandas
        :param labels: list
        :param labels: list: 
        :returns: pandas.DataFrame: Sanitized data

        """
        data = data.apply(pd.to_numeric, errors='coerce')
        data.dropna(inplace=True)
        data.index = pd.to_numeric(data.index)
        data.columns=labels
        return data
        
    def load_csv_data(self, wavelength: int, basedir=None, start=0., 
                      regex=None, encoding='iso-8859-1'):
        """Reads a series of fluorescence spectra from CSV files
        (Exported from Cary Eclipse, for now.)

        :param wavelength: The wavelength of excitation
        :param should: be specified in the filename
        :param basedir: The path to where the files are located (Default value = None)
        :param start: Which data should be dropped from importing (Default value = 0.)
        :param regex: Regular expression used to extract concentration (Default value = None)
        :param encodig: In which encoding is the file
        :param wavelength: int: 
        :param encoding:  (Default value = 'iso-8859-1')

        """

        self.data = pd.DataFrame()
        regex = regex
        if regex is None:
            i = 0
        for file in glob(f"{basedir}*{wavelength}.csv"):
            if regex is not None:
                conc = float(re.findall(regex, file)[0])
                conc = round(conc*22/(2000+conc),2)
                if conc <= start:
                    continue
            else:
                i = i + 1
                conc = i
            
            col = Spectra.sanitize_columns(pd.read_csv(file,encoding=encoding,index_col=0,header=1,
                                  usecols=[0,1]), [conc])
            self.data = pd.concat((self.data,col), axis=1)

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
        """Plots the specified number (nearest value).

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

    def decorate_plot(self, ylabel=None, style=None):
        """Sets plot title, ylabel and legend title.

        :param style:  (Default value = None)

        """
        plt.legend(title = self.legend_title, frameon='none', edgecolor='none')
        plt.title(self.title)
        if ylabel is None:
            ylabel = self.ylabel
        plt.ylabel(ylabel)


    def normalize_data(self, fun=lambda x: x/max(x)):
        """Normalizes the data applying the specified lambda."""
        self.normdata = self.data.apply(fun)
    
    def plot_normalized(self, style=None):
        """

        :param style:  (Default value = None)

        """
        if self.normdata is None:
            self.normalize_data()
        
        self.normdata.plot(style=style)
        self.decorate_plot(ylabel="Norm. intensity (a.u.)")
        plt.ylim([0, 1])

    def plot_maxima(self, style=None):
        """Plots the maximum wavelength vs. column.

        :param style:  (Default value = None)

        """
        maxima = self.data.idxmax()
        maxima.plot(style=style)
        self.decorate_plot()