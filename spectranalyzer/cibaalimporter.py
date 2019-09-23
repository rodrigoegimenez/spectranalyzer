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

import os
import pandas as pd
import chardet

class CibaalImporter():
    def __init__(self, file, tipo):
    #    f = open(file, 'r')
        if (tipo == "CaryOld"):
            self.data = pd.read_csv(file, index_col=0, skiprows=1, usecols=[0,1])
            self.title = file.split(os.path.sep)[-1][:-4]
            self.title = self.title.split()[0].replace('-', '.')
            if "C" in self.title:
                self.title = self.title[:-1]
            self.title = float(self.title)
        if (tipo == "Cary"):
            # We first get the encoding of the file
            encoding = None
            with open(file, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result["encoding"]
                
            # We read the CSV file and convert it to numeric
            self.data = pd.read_csv(file, skiprows=1, usecols=[0,1],
                                    error_bad_lines=False, encoding=encoding)
            self.data[self.data.columns[0]] = pd.to_numeric(self.data[self.data.columns[0]],errors="coerce")
            self.data[self.data.columns[1]] = pd.to_numeric(self.data[self.data.columns[1]],errors="coerce")
            
            self.data.dropna(inplace=True)
            self.data.set_index(self.data.columns[0], inplace=True)
            
            #We delete the ".csv" part from the file and set it as title
            self.title = file.split(os.path.sep)[-1][:-4]
            self.title = self.title.split()[0].replace('-', '.')
            if "C" in self.title:
                self.title = self.title[:-1]
                self.title = float(self.title)