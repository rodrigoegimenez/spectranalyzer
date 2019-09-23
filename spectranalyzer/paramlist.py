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

class ParamList():
    def __init__(self):
        self.params = []
    
    def append(self, item):
        self.params.append(item)
    
    def values(self, parameter):
        values = []
        for item in self.params:
            values.append(item[parameter].value)
        return values
    
    def stderrs(self, parameter):
        values = []
        for item in self.params:
            values.append(item[parameter].stderr)
        return values