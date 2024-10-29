

class LabeledSliceDisplay:
    """
    Visualize slices of volume data.
    """
    cmap = CMAP_DEFAULT_CT
    auto_arraycast: bool = True
    auto_squeeze: bool = True

    def __init__(self, volume: Array, labels: Dict[str, Array]) -> None:
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot()
        
        self.volume = preprocess_array(volume, self.auto_arraycast,
                                       self.auto_squeeze)
        self.img = self.ax.imshow(
            self.volume.data[0, ...], vmin=self.volume.stats.min,
            vmax=self.volume.stats.max, cmap=self.cmap
        )
        
        labels = {
            name : preprocess_array(array, self.auto_arraycast, self.auto_squeeze)
            for name, array in labels.items()
        }
        self.overlays= LabelOverlayContainer.from_dict(labels, self.ax)
        
        self.slider = self._init_slider()
        self.axis_selector = self._init_axis_selector()

    
    def _init_slider(self) -> wgt.IntSlider:
        """First-time initialization of slider"""
        slider = create_slider(self.volume.data)
        self.connect_slider(slider)
        return slider

    
    def _init_axis_selector(self) -> wgt.Dropdown:
        """First-time initialization of dropdown selector"""
        selector = create_axis_selector(self.volume)
        self.connect_axis_selector(selector)
        return selector


    def _reinit_slider(self) -> None:
        """Reininitialize preexisting slider. Useful if data shape changes."""
        try:
            slider = getattr(self, 'slider')
        except AttributeError as e:
            msg = 'Slider is not existing. Use _reinit only after initialization'
            raise RuntimeError(msg) from e        
        # Deduce slider maximum settable value from data primary axis. 
        slider.max = self.volume.data.shape[0] - 1
        slider.value = 0

        self.ax.relim()
        self.ax.autoscale()
        self.fig.canvas.draw_idle()

    
    def connect_slider(self, slider: wgt.IntSlider):

        def on_slider_value_change(change):
            new_idx = change['new']
            self.img.set_data(self.volume.data[new_idx, ...])
            self.overlays.allset_index(new_idx)
            self.fig.canvas.draw_idle()
            return

        slider.observe(on_slider_value_change, names='value')


    def connect_axis_selector(self, axis_selector):

        def on_axis_selector_value_change(change):
            new_axis = change['new']
            self.volume.primary_axis = new_axis
            self.overlays.allset_axis(new_axis)
            self._reinit_slider()
            return
        
        axis_selector.observe(on_axis_selector_value_change, names='value')
    

    def get_controls(self, selector: str = 'all') -> wgt.HBox:
        """
        Get the controls as a nicely laid out horizontal widget box.
        """
        general_controls = wgt.HBox([self.slider, self.axis_selector])
        overlay_controls = self.overlays.get_control_tabs()
        return wgt.VBox([general_controls, overlay_controls])

    
    @classmethod
    def from_result(cls, result: Result, reduction: Union[int, str]) -> 'LabeledSliceDisplay':
        """
        Create an instance directly from a `Result` object. The reduction argument
        allows selection of samples (integer index) or reduction (string 'mean' or 'variance')
        of supersampled predictions.
        Here, raw data is used, together with the annotated volume label and the 
        segmentation prediction.

        Parameters
        ----------

        result : Result
            The result object from which raw, label and prediction data
            is read.

        reduction : string or integer
            Allows selection or reduction of samples for a supersampled
            prediction. The argument has no effect if the prediction is not
            supersampled.

        Returns
        -------

        LabeledSliceDisplay
        """
        # extract relevant data from result
        raw = result.annotated_volume.raw
        label = result.annotated_volume.label
        segmentation = get_segmentation_helper(result.prediction, reduction)
        labels = {'gt' : label, 'pred' : segmentation}
        return cls(raw, labels)