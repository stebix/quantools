"""
Tooling to programmatically interact with parsed segmentation information.

@Author: Jannik Stebani 2024
"""
from collections.abc import Mapping
from typing import Literal

import attrs
import numpy as np


from quantools.segmentinfo.unit import Unit

@attrs.define
class ParameterROI:
    name: str
    values: np.ndarray = attrs.field(repr=lambda arr: arr.shape)
    unit: Unit


@attrs.define
class TissueROI:
    name: str
    T1: ParameterROI
    T2: ParameterROI
    M0: ParameterROI
    IP: ParameterROI
    mask: np.ndarray = attrs.field(repr=lambda arr: f'(shape={arr.shape}, dtype={arr.dtype}')
    volume: int = attrs.field(init=False)
        
    def __attrs_post_init__(self):
        self.volume = np.sum(self.mask)
        
    def __getitem__(self, item_name: str) -> ParameterROI | np.ndarray:
        mapping = {'T1' : self.T1, 'T2' : self.T2, 'M0' : self.M0, 'IP' : self.IP, 'mask' : self.mask}
        return mapping[item_name]
    
    @classmethod
    def create_from(cls, name: str, maps: Mapping[str, np.ndarray], mask: np.ndarray, unit: str | Unit = 'seconds'):
        """Create single tissue ROI specification."""
        if not isinstance(unit, Unit):
            unit = Unit(unit)
            
        T1 = ParameterROI(name='T1', values=maps['T1'][mask], unit=unit)
        T2 = ParameterROI(name='T2', values=maps['T2'][mask], unit=unit)
        M0 = ParameterROI(name='M0', values=maps['M0'][mask], unit=unit)
        IP = ParameterROI(name='IP', values=maps['IP'][mask], unit=unit)

        return cls(name=name, T1=T1, T2=T2, M0=M0, IP=IP, mask=mask)
    
    def __iter__(self):
        return iter([self.T1, self.T2, self.M0, self.IP])

    
@attrs.define
class Segmentation:
    tissues: list[TissueROI]
        
    sort: Literal['none', 'increasing', 'decreasing'] = 'decreasing'
        
    def __attrs_post_init__(self):
        if self.sort == 'none':
            return
        self.tissues = list(sorted(self.tissues, key=lambda tissue: tissue.volume))
        if self.sort == 'decreasing':
            self.tissues = list(reversed(self.tissues))
        return
        
    def __iter__(self):
        return iter(self.tissues)
    
    def __getitem__(self, item: int | str) -> TissueROI:
        """
        Retrieve tissue by integer index into list or by name.
        If name is present multiple times, the first matching tissue ROI is returned.
        """
        if isinstance(item, int):
            return self.tissues[item]
        
        names = [tissue.name for tissue in self.tissues]
        return self.tissues[names.index(item)]
        
    
    @classmethod
    def create_from(cls, parameters: Mapping[str, np.ndarray], masks: Mapping[str, np.ndarray]):
        tissues = []
        for tissue_name, mask in masks.items():
            tissues.append(
                TissueROI.create_from(name=tissue_name, maps=parameters, mask=mask)
            )
        return cls(tissues=tissues)