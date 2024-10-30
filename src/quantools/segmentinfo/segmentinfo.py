"""
Tooling to programmatically interact with parsed segmentation information.

@Author: Jannik Stebani 2024
"""
from collections.abc import Mapping
from typing import Literal

import attrs
import numpy as np


from quantools.segmentinfo.unit import Unit

def value_repr(obj) -> str:
    if isinstance(obj, np.ndarray):
        return f'(shape={obj.shape}, dtype={obj.dtype})'
    else:
        return str(obj)


@attrs.define
class ParameterROI:
    name: str
    values: np.ndarray | None = attrs.field(repr=value_repr)
    unit: Unit


@attrs.define
class TissueROI:
    name: str
    parameters: dict[str, ParameterROI]
    mask: np.ndarray = attrs.field(repr=lambda arr: f'(shape={arr.shape}, dtype={arr.dtype}')
    volume: int = attrs.field(init=False)
        
    def __attrs_post_init__(self):
        self.volume = np.sum(self.mask)
        
    def __getitem__(self, item_name: str) -> ParameterROI | np.ndarray:
        mapping = {**self.parameters, 'mask' : self.mask, 'name' : self.name, 'volume' : self.volume}
        return mapping[item_name]
    
    def __iter__(self):
        return iter(self.parameters.values())
    
    @classmethod
    def create_from(cls, name: str, maps: Mapping[str, np.ndarray], mask: np.ndarray, unit: str | Unit = 'seconds'):
        """Create single tissue ROI specification."""
        if not isinstance(unit, Unit):
            unit = Unit(unit)

        parameters = {}
        canonical_parameters = [('T1', unit), ('T2', unit), ('M0', Unit.NONE), ('IP', Unit.NONE)]
        for parameter_name, parameter_unit in canonical_parameters:
            try:
                values = maps[parameter_name][mask]
            except (TypeError, KeyError):
                continue

            parameters[parameter_name] = ParameterROI(name=parameter_name,
                                                      values=values,
                                                      unit=parameter_unit)
        
        return cls(name=name, mask=mask, parameters=parameters)
    

    
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