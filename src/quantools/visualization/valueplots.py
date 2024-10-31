"""
Tooling to plot errorbars of T1 and T2 relaxation times, magnetization values, and inner product values.

@Author: Jannik Stebani 2024
"""
from collections.abc import Mapping
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from quantools.segmentinfo.unit import Unit
from quantools.visualization.utils import get_value_and_uncert


def plot_parameter_single(tissues: Mapping[str, Mapping[str, float]],
                          parameter_name: str,
                          ax: Axes | None = None,
                          xlabel: str | None = None,
                          ylabel: str | None = None,
                          unit: Literal['seconds', 'milliseconds'] = 'seconds',
                          ylim: tuple[float, float] | None = None,
                          capsize: float = 5,
                          restrict_errors: bool = True,
                          prefix: str = '',
                          postfix: str = ''
                          ) -> tuple[Figure, Axes]:
    """
    Plot parameter categorically into single plot.
    Geared towards tissues of a single series.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        ax = ax
        fig = ax.get_figure()
        
    unit = Unit(unit)
    unit_str = 's' if unit is Unit.SECONDS else 'ms'
    labels = {
        'xlabel' : 'Tissue Index',
        'ylabel' : 'Parameter Value'
    }
    if xlabel:
        labels.update({'xlabel' : xlabel})
    if ylabel:
        labels.update({'ylabel' : ylabel})
            
    for index, (tissue_name, tissue_statistics) in enumerate(tissues.items()):

        value = tissue_statistics[parameter_name]['mean']
        uncert = tissue_statistics[parameter_name]['stdev']

        if restrict_errors:
            diff = value - uncert
            uncert = uncert + diff if diff < 0 else uncert

        display_tissue_name = f'{prefix}{tissue_name}{postfix}'

        ax.errorbar(tissue_name, value,
                    yerr=uncert, label=display_tissue_name, marker='o',
                    capsize=capsize)
        
    kwargs = {'ylim' : ylim}
    ax.set(**labels, **kwargs)
    ax.legend()
    return (fig, ax)



def plot_T1_single(tissues: Mapping[str, Mapping[str, float]],
                   ax: Axes | None = None,
                   xlabel: str | None = None,
                   ylabel: str | None = None,
                   unit: Literal['seconds', 'milliseconds'] = 'seconds',
                   ylim: tuple[float, float] = (1.75, 5.0),
                   restrict_errors: bool = True,
                   prefix: str = '',
                   postfix: str = '',
                   **kwargs
                   ) -> tuple[Figure, Axes]:
    
    unit = Unit(unit)
    unit_str = 's' if unit is Unit.SECONDS else 'ms'
    labels = {
        'xlabel' : 'Tissue Index',
        'ylabel' : f'$T_1$ spin-lattice relaxation time [{unit_str}]'
    }
    return plot_parameter_single(tissues, parameter_name='T1', ax=ax, **labels,
                                 unit=unit, ylim=ylim, restrict_errors=restrict_errors,
                                 prefix=prefix, postfix=postfix,
                                 **kwargs)



def plot_T2_single(tissues: Mapping[str, Mapping[str, float]],
                   ax: Axes | None = None,
                   xlabel: str | None = None,
                   ylabel: str | None = None,
                   unit: Literal['seconds', 'milliseconds'] = 'seconds',
                   ylim: tuple[float, float] = (0.01, 2.0),
                   restrict_errors: bool = True,
                   prefix: str = '',
                   postfix: str = '',
                   **kwargs
                   ) -> tuple[Figure, Axes]:
    
    unit = Unit(unit)
    unit_str = 's' if unit is Unit.SECONDS else 'ms'
    labels = {
        'xlabel' : 'Tissue Index',
        'ylabel' : f'$T_2$ spin-spin relaxation time [{unit_str}]'
    }
    return plot_parameter_single(tissues, parameter_name='T2', ax=ax, **labels,
                                 unit=unit, ylim=ylim, restrict_errors=restrict_errors,
                                 prefix=prefix, postfix=postfix,
                                 **kwargs)



def plot_grouping(elements: Mapping[str, dict[str, float]],
                  ax: Axes | None = None,
                  xaxis: Literal['T1', 'T2'] = 'T1',
                  yaxis: Literal['T1', 'T2'] = 'T2',
                  capsize: float = 5,
                  unit: Literal['seconds', 'milliseconds'] = 'seconds',
                  prefix: str = '',
                  postfix : str = '',
                  marker: str = 'o',
                  axtitle: str = '',
                  restrict_errors: bool = True
                  ) -> tuple[Figure, Axes]:
    """
    Plot grouping of values in (T1, T2) axes.
    
    Parameters
    ----------

    elements : Mapping[str, dict[str, float]]
        Mapping of element names to dictionaries of T1 and T2 values.

    ax : Axes | None, optional
        Matplotlib axes object. If None, a new figure is created.
        Default is None.

    xaxis : Literal['T1', 'T2'], optional
        X axis takes this value. Default is 'T1'.

    yaxis : Literal['T1', 'T2'], optional
        Y axis takes this value. Default is 'T2'.

    capsize : float, optional
        Errorbar capsize. Default is 5.

    unit : Literal['seconds', 'milliseconds'], optional
        Unit of the relaxation times. Default is 'seconds'.

    prefix : str, optional
        Prefix to add to the element names. Can be used to disambiguate
        different groups of elements. Default is ''.

    postfix : str, optional
        Postfix to add to the element names. Can be used to disambiguate
        different groups of elements. Default is ''.

    marker : str, optional
        Marker style for the errorbars. Default is 'o'.

    axtitle : str, optional
        Title of the axes. Default is ''.

    restrict_errors: bool, optional
        If True, restrict errorbars to positive values. Default is True.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        ax = ax
        fig = ax.get_figure()
        
    unit = Unit(unit)
    unit_str = 's' if unit is Unit.SECONDS else 'ms'
    t1_lbl = f'$T_1$ spin-lattice relaxation time [{unit_str}]'
    t2_lbl = f'$T_2$ spin-spin relaxation time [{unit_str}]'
    
    if xaxis == 'T1' and yaxis == 'T2':
        xlabel = t1_lbl
        ylabel = t2_lbl
    else:
        xlabel = t2_lbl
        ylabel = t1_lbl
    labels = {'xlabel' : xlabel, 'ylabel' : ylabel}
    
    for name, parameters in elements.items():
        T1_value, T1_uncert = get_value_and_uncert('T1', parameters)
        T2_value, T2_uncert = get_value_and_uncert('T2', parameters)
        
        if xaxis == 'T1' and yaxis == 'T2':
            x, xerr = T1_value, T1_uncert
            y, yerr = T2_value, T2_uncert
        elif xaxis == 'T2' and yaxis == 'T1':
            x, xerr = T2_value, T2_uncert
            y, yerr = T1_value, T1_uncert
        else:
            raise ValueError(f'invalid axis specification: {xaxis} and {yaxis}')
        
        if restrict_errors:
            xdiff = x - xerr
            ydiff = y - yerr
            xerr = xerr + xdiff if xdiff < 0 else xerr
            yerr = yerr + ydiff if ydiff < 0 else yerr
        
        label = f'{prefix}{name}{postfix}'
        ax.errorbar(x, y, xerr=xerr, yerr=yerr, marker=marker,
                    capsize=capsize, label=label)
    
    ax.legend()
    ax.set(**labels)
    ax.set_title(axtitle)
    return (fig, ax)