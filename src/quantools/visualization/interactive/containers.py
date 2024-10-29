import matplotlib
import numpy as np
import ipywidgets as wgt
from cycler import Cycler, cycler


# Default property cyclers for LabelOverlayContainer classmethod
LABEL_COLOR_SEQUENCE = ('#03fc20', '#fc0303', '#0307fc', '#f003fc')
LABEL_ALPHA_SEQUENCE = (1.0, 0.60, 0.33, 0.33)
# cycle over 'value' argument: relevant keyword for ipywidgets instances
DEFAULT_COLOR_CYCLE = cycler(value=LABEL_COLOR_SEQUENCE)
DEFAULT_ALPHA_CYCLE = cycler(value=LABEL_ALPHA_SEQUENCE)


def hex_to_rgb(hexcolor):
    """
    Convert hexadecimal color strings to RGB float tuple.
    #32a852 -> (0.20, 0.66, 0.32)

    Parameters
    ----------

    hexcolor : str
        Color as string specification.

    Returns
    -------

    rgb : tuple of float
        The converted RGB float tuple.
    """
    hexcolor = hexcolor.lstrip('#')
    hexcolor_rgb = []
    for i in (0, 2, 4):
        elem = int(hexcolor[i:i+2], 16) / 255
        hexcolor_rgb.append(elem)
    return tuple(hexcolor_rgb)


def create_alpha_cmap(base_color, max_alpha=1.0, alpha_ticks=50):
    """
    Construct a single-color colormap that provides a smooth
    increase of the alpha value from 0 to max_alpha for the
    desired color.

    Parameters
    ----------
    
    base_color : tuple
        RGB color specification as tuple of three floats
        in [0, 1]
    
    max_alpha : float, optional
        Maximum alpha value. Set < 1 if
        transparency at max value is desired.
    
    alpha_ticks : int, optional
        Number of steps along the alpha
        transparency axis.
    
    Returns
    -------

    alpha_map : matplotlib.colors.Colormap
        The colormap instance.
    """
    alpha_range = np.linspace(0, max_alpha, num=alpha_ticks)[:, np.newaxis]
    rgb_arr = np.array((base_color))[np.newaxis, :]    
    
    colorspec = np.concatenate(
        [np.broadcast_to(rgb_arr, (alpha_range.shape[0], 3)), alpha_range],
        axis=-1
    )
    msg = f'Expected {(alpha_ticks, 4)}, got {colorspec.shape}'
    assert colorspec.shape == (alpha_ticks, 4), msg
    return matplotlib.colors.ListedColormap(colorspec)


def create_colorpicker(name: str, **kwargs) -> wgt.ColorPicker:
    """
    Create a colorpicker instance. Any keyword arguments collected
    in `kwargs` are passed through to the `ipywidgets.ColoPicker`
    initializer.
    """
    # default settings, are updated with function kwargs
    picker_kwargs = {'concise' : False, 'description' : f'{name} color',
                     'value' : '#ff5733'}
    picker_kwargs.update(kwargs)
    return wgt.ColorPicker(**picker_kwargs)


def create_alphaslider(name: str, **kwargs) -> wgt.FloatLogSlider:
    """
    Create a slider instance for alpha value selection.
    Any keyword arguments collected in `kwargs` are
    passed through to the `ipywidgets.ColoPicker` initializer.
    """
    # default settings, are updated with function kwargs
    slider_kwargs = {'value' : 1.0, 'min' : 0.0,
                     'max' : 1.0, 'description' : f'{name} alpha'}
    slider_kwargs.update(kwargs)
    return wgt.FloatSlider(**slider_kwargs)



class LabelOverlay:
    """
    Implement overlaid crisp label data. Connection to parent
    figure via reference to `parent_ax` instance.

    Parameters
    ----------

    name : str
        The name of the label overlay. E.g. 'ground truth'
        or 'prediction'.

    labelarray :  TrackedArray
        The numerical array data. Should have a 3D numpy.ndarray
        as basal data.

    parent_ax : matplotlib.axes.Axes
        The axes into which the label overlay `imshow` method
        call will be drawn.
    
    colorpicker_kwargs : dict, optional
        Keyword arguments are forwarded to the 
        `ipywidgets.ColorPicker` initializer.
    
    alphaslider_kwargs : dict, optional
        Keyword arguments are forwarded to the 
        `ipywidgets.FloatSlider` initializer.
    """
    def __init__(self,
                 name: str,
                 labelarray: np.ndarray,
                 parent_ax: matplotlib.axes.Axes,
                 colorpicker_kwargs: dict | None = None,
                 alphaslider_kwargs: dict | None = None) -> None:
        
        self.name = name
        self.labelarray = labelarray
        self.img = parent_ax.imshow(labelarray.data[0, ...],
                                    vmin=0, vmax=1, cmap=self._init_cmap())
        self.parent_ax = parent_ax
        colorpicker_kwargs = colorpicker_kwargs or {}
        alphaslider_kwargs = alphaslider_kwargs or {}
        self.colorpicker = self._init_colorpicker(**colorpicker_kwargs)
        self.alphaslider = self._init_alphaslider(**alphaslider_kwargs)
    
    def _init_colorpicker(self, **kwargs) -> wgt.ColorPicker:
        """
        Initialize colorpicker: kwarg passthrough and
        connection via observe
        """
        colorpicker = create_colorpicker(self.name, **kwargs)
        self.connect_colorpicker(colorpicker)
        return colorpicker
    
    def _init_alphaslider(self, **kwargs) -> wgt.FloatSlider:
        """
        Initialize alphaslider: kwarg passthrough and
        connection via observe
        """
        alphaslider = create_alphaslider(self.name, **kwargs)
        self.connect_alphaslider(alphaslider)
        return alphaslider
    
    def _init_cmap(self) -> matplotlib.colors.Colormap:
        return create_alpha_cmap((1, 0, 0), 0.25)
    
    def setindex(self, new_index: int) -> None:
        self.img.set_data(self.labelarray.data[new_index, ...])
        
    def setaxis(self, new_axis: str) -> None:
        self.labelarray.primary_axis = new_axis
    
    def get_controlpanel(self) -> wgt.HBox:
        """Control panels (alphaslider, colorpicker) wrapped inside HBox"""
        return wgt.HBox([self.alphaslider, self.colorpicker])
        
    def connect_colorpicker(self, colorpicker):
        
        def modify_color(change):
            """
            Set the colormap of `axes_img` to a alpha colormap with
            the base color deduced from `change`.
            """
            color = hex_to_rgb(change['new'])
            cmap = create_alpha_cmap(color, self.alphaslider.value)
            self.img.set_cmap(cmap)
            self._draw_call()
        
        colorpicker.observe(modify_color, names='value')
        
    def connect_alphaslider(self, alphaslider):
        
        def modify_alpha(change):
            color = hex_to_rgb(self.colorpicker.value)
            cmap = create_alpha_cmap(color, change['new'])
            self.img.set_cmap(cmap)
            self._draw_call()
        
        alphaslider.observe(modify_alpha, names='value')
        
    def _draw_call(self) -> None:
        self.parent_ax.get_figure().canvas.draw_idle()




class LabelOverlayContainer:  
    """
    Container class for multiple LabelOverlay instances.
    Allows bulk interaction via `allset_index` and `allset_axis`
    methods and handles joint control panel creation via
    `get_control_tabs`

    Parameters
    ----------

    label_overlays : Sequence of LabelOverlay
        The overlays managed by this container. Note that the drawing
        z-order is determined by the input order here. Last input gets drawn
        on top.
    """
    def __init__(self, *label_overlays: LabelOverlay) -> None:
        self._container = {lo.name : lo for lo in label_overlays}
    
    def allset_index(self, new_index: int) -> None:
        for lo in self._container.values():
            lo.setindex(new_index)
    
    def allset_axis(self, new_axis: str) -> None:
        for lo in self._container.values():
            lo.setaxis(new_axis)
    
    def get_control_tabs(self) -> wgt.Tab:
        """
        Get joint control panel of the all label overlays organized
        in a wgt.Tab layout instance.
        """
        titles = [name for name in self._container.keys()]
        children = [lo.get_controlpanel() for lo in self._container.values()]
        tab = wgt.Tab()
        tab.children = children
        for i, title in enumerate(titles):
            tab.set_title(i, title)
        return tab
            
    def __getitem__(self, key):
        return self._container[key]
    
    @classmethod
    def from_dict(cls,
                  labels: dict[str, np.ndarray],
                  ax: matplotlib.axes.Axes,
                  colorpropcycle: cycler | None = None,
                  alphapropcycle: cycler | None = None) -> 'LabelOverlayContainer':
        """
        Create a `LabelOverlayContainer` instance automatically from a dictionary
        mapping string names to tracked arrays.

        Parameters
        ----------

        labels : Dict[str, TrackedArray]
            Dictionary that maps label names to label 3D data in the format
            of TrackedArray instances.

        ax : matplotlib.axes.Axes
            The ax into which the label overlays will be drawn via the
            `imshow` method.

        colorpropcycle : Cycler, optional
            Determines the sequence of initial label colors.
            Defaults to 4-element default from module constant.

        alphapropcycle : Cycler, optional
            Determines the sequence of initial label alpha values.
            Defaults to 4-element default from module constant.
        """
        labeloverlays = []
        colorcycler = colorpropcycle or DEFAULT_COLOR_CYCLE
        alphacycler = alphapropcycle or DEFAULT_ALPHA_CYCLE
        cyclers = zip(colorcycler, alphacycler)
        for (name, trackedarray), (colorkwargs, alphakwargs) in zip(labels.items(), cyclers):
            labeloverlays.append(
                LabelOverlay(name, trackedarray, ax,
                             colorpicker_kwargs=colorkwargs,
                             alphaslider_kwargs=alphakwargs)
            )
        return cls(*labeloverlays)
