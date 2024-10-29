"""
Tooling to plot histograms of T1 and T2 relaxation times, magnetization values, and inner product values.

@Author: Jannik Stebani 2024
"""
from collections.abc import Mapping
from typing import Literal

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

from matplotlib.axes import Axes
from matplotlib.figure import Figure

from quantools.segmentinfo.segmentinfo import Segmentation, TissueROI
from quantools.segmentinfo.unit import Unit
from quantools.visualization.utils import (PARAMETER_NAME_REMAPPING,
                                           get_canonical_axis_label,
                                           get_color)


def draw_histogram(data: np.ndarray,
                   tissue_label: str,
                   parameter_label: str,
                   parameter_unit: str,
                   ax: Axes,
                   bins: int,
                   draw_mean: bool = True,
                   color: str | None = None) -> Axes:
    """Draw histogram into preexisting axes"""
    mean = data.mean()
    unit = f' {parameter_unit}' if parameter_unit else ''
    label = f'{tissue_label} ' + '$\\langle$' + f'{parameter_label}' + '$\\rangle$' + f' = {mean:.3f}{parameter_unit}'

    _, _, patches = ax.hist(data, bins=bins, label=label, color=color)
    color = get_color(patches)
    
    if draw_mean:    
        ax.axvline(x=mean, color=color, dashes=[4, 4], gapcolor='black', alpha=0.8)    



def plot_parameter(segmentation: Segmentation,
                   parameter_name: str = 'T2',
                   ax: Axes | None = None,
                   bins: int = 60,
                   xlabel: str | None = None,
                   ylabel: str | None = None,
                   yscale: str = 'linear',
                   parameter_remapping: Mapping | None = None,
                   suptitle: str = ''
                  ) -> tuple[Figure, Axes]:
    if ax is None:
        fig, ax = plt.subplots()
    else:
        ax = ax
        fig = ax.get_figure()

    ax.set_yscale(yscale)
    
    parameter_remapping = PARAMETER_NAME_REMAPPING | (parameter_remapping or {})
    
    for tissue in segmentation:
        parameter = tissue[parameter_name]
        
        if parameter.unit == Unit.SECONDS:
         unit = 's'
        elif parameter.unit == Unit.MILLISECONDS:
            unit = 'ms'
        else:
            unit = ''
            
        labels = get_canonical_axis_label(parameter_name, unit=unit)
        if xlabel:
            labels.update({'xlabel' : xlabel})
        if ylabel:
            labels.update({'ylabel' : ylabel})
            
        remapped_parameter_label = parameter_remapping.get(parameter.name, parameter.name)
            
        draw_histogram(
            data=parameter.values, tissue_label=tissue.name, parameter_label=remapped_parameter_label, parameter_unit=unit,
            bins=bins, draw_mean=True, ax=ax
        )
    
    ax.set(**labels)
    ax.legend()
    fig.suptitle(suptitle)
    fig.tight_layout()
    return (fig, ax)




def plot_2D_histogram(tissue: TissueROI,
                      ax: Axes | None = None,
                      xaxis: Literal['T1', 'T2'] = 'T1',
                      yaxis: Literal['T1', 'T2'] = 'T2',
                      bins: int = 100,
                      title: str = '',
                      gamma: float = 0.3,
                      unit: Literal['seconds', 'milliseconds'] = 'seconds'
                     ) -> tuple[Figure, Axes]:
    """Plot 2D heatmap/histogram of T1 and T2 data for single tissue"""
    if ax is None:
        fig, ax = plt.subplots()
    else:
        ax = ax
        fig = ax.get_figure()
        
    T1 = tissue.T1.values
    T2 = tissue.T2.values
    
    unit = Unit(unit)
    unit_str = 's' if unit is Unit.SECONDS else 'ms'
    t1_lbl = f'$T_1$ spin-lattice relaxation time [{unit_str}]'
    t2_lbl = f'$T_2$ spin-spin relaxation time [{unit_str}]'
    
    if xaxis == 'T1' and yaxis == 'T2':
        x = T1
        y = T2
        xlabel = t1_lbl
        ylabel = t2_lbl
        
    elif xaxis == 'T2' and yaxis == 'T1':
        x = T2
        y = T1
        xlabel = t2_lbl
        ylabel = t1_lbl
    else:
        raise ValueError('invalida axis specification: must be T1 or T2 per axis')
    
    labels = {'xlabel' : xlabel, 'ylabel' : ylabel}
    norm = colors.PowerNorm(gamma)
    ax.hist2d(x, y, bins=bins, norm=norm)
    ax.set(**labels)
    ax.set_title(title)
    return (fig, ax)