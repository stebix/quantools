"""
Visualization utilities for the quantools package.

@Author: Jannik Stebani 2024
"""
import warnings
from string import Template


class TexCompliantTemplate(Template):
    delimiter: str = '§'


PARAMETER_NAME_REMAPPING: dict[str, str] = {
    'T1' : '$T_1$',
    'T2' : '$T_2$',
    'M0' : '$M_0$'
}


CANONICAL_AXIS_LABELS: dict[str, dict[str]] = {
    'T1' : {
        'x' : TexCompliantTemplate('$T_1$ spin-lattice relaxation time [§unit]'),
        'y' : TexCompliantTemplate('Absolute frequency')
    },
    'T2' : {
        'x' : TexCompliantTemplate('$T_2$ spin-spin relaxation time [§unit]'),
        'y' : TexCompliantTemplate('Absolute frequency')
    },
    'M0' : {
        'x' : TexCompliantTemplate('$M_0$ magnetization [a.u.]'),
        'y' : TexCompliantTemplate('Absolute frequency')
    },
    'IP' : {
        'x' : TexCompliantTemplate('Inner product value [a.u.]'),
        'y' : TexCompliantTemplate('Absolute frequency')
    }
}


CANONICAL_COLOR_SPECIFICATION: dict[str, str] = {
    'cochlea' : 'tab:green',
    'vestibulum' : 'gold',
    'nerve' : 'tab:blue',
    'canals' : 'tab:red'
}

SLICER_COLOR_SPECIFICATION: dict[str, str] = {
    'cochlea' : '#80ae80',
    'vestibulum' : '#f1d691',
    'canals' : '#b17a65',
    'nerve' : '#6fb8d2'
}
    

def get_canonical_axis_label(parameter_name: str, unit: str):
    labels = {}
    axes = {'xlabel' : 'x', 'ylabel' : 'y'}
    for key, axis in axes.items():
        try:
            label = CANONICAL_AXIS_LABELS[parameter_name][axis].substitute(unit=unit)
        except AttributeError:
            label = CANONICAL_AXIS_LABELS[parameter_name][axis]
            
        labels[key] = label
    
    return labels
    

def get_color(patches) -> tuple[float, float, float]:
    """Get color of patch(es) in a bar container (i.e. `ax.hist` return value)"""
    patch = patches.patches[0]
    return patch.get_facecolor()


def get_value_and_uncert(name: str, parameters: dict[str, dict[str, float]]) -> tuple[float, float]:
    value = parameters[name]['mean']
    uncert = parameters[name]['stdev']
    return (value, uncert)


def get_canonical_tissue_color(name: str) -> str | None:
    try:
        return SLICER_COLOR_SPECIFICATION[name.lower()]
    except KeyError:
        warnings.warn(f'No canonical color specification for tissue "{name}".')
        return None