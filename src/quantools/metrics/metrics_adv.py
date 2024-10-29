"""
Tooling for computing statistics with direct interfacing with segmentation information.

@Author: Jannik Stebani 2024
"""
from quantools.metrics.metrics_raw import compute_statistical_parameters
from quantools.segmentinfo.segmentinfo import Segmentation, TissueROI



def compute_volume(tissue: TissueROI) -> dict:
    parameter = next(iter(tissue))
    return {'volume' : parameter.values.size}


def compute_tissue_statistics(tissue: TissueROI) -> dict:
    parameter_statistics = {}
    for parameter in tissue:
        parameter_statistics[
            parameter.name
        ] = compute_statistical_parameters(parameter.values)
    
    statistics = {tissue.name : parameter_statistics}
    statistics[tissue.name].update(compute_volume(tissue))
    return statistics


def compute_statistics(data: Segmentation | TissueROI):
    if isinstance(data, TissueROI):
        return compute_tissue_statistics(data)
    statistics = {}
    for tissue in data:
        statistics.update(compute_tissue_statistics(tissue))
    return statistics