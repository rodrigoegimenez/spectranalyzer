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
import json

class Fitter():
    def __init__(self, name="Fitter"):
        self.fits = []
        self.name = name
    
    def load_data_from_json(self, data):
        df = pd.DataFrame()
        for item in data:
            df = df.append(pd.Series(index=item['x'], data=item['y'], name=item['name']),)
        self.df = df.transpose()

    def load_file(self, filename, xlabel=None):
        self.name = filename.replace(".csv",
                                     "").replace(".xlsx",
                                                 "").replace(".xls", "")
        self.df = pd.read_csv(filename, index_col=0)
        self.sanitize_data()
        self.report = pd.DataFrame()
        self.xlabel = xlabel

    def sanitize_data(self):
        self.sanitize_columns()
        self.sanitize_index()
        self.df.replace(to_replace=",", value=".", regex=True, inplace=True)
        self.df = self.df.apply(pd.to_numeric)
        self.df.dropna(how='all', inplace=True)
        self.df.dropna(how='all', axis=1, inplace=True)

    def sanitize_columns(self):
        newcols = []
        for col in self.df.columns:
            if type(col) is str and "," in col:
                col = col.replace(",", ".")
            newcols.append(float(col))
        self.df.columns = newcols

    def sanitize_index(self):
        newidx = []
        for idx in self.df.index:
            if type(idx) is str and "," in idx:
                idx = idx.replace(",", ".")
            newidx.append(float(idx))
        self.df.index = newidx
