import matplotlib
import numpy as np

from matplotlib.axes import Axes


def get_color(patches) -> tuple[float, float, float]:
    """Get color of patch(es) in a bar container (i.e. `ax.hist` return value)"""
    patch = patches.patches[0]
    return patch.get_facecolor()



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