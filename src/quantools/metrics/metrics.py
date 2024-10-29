"""
Compute quantitative metrics for maps.

@Author: Jannik Stebani
"""

def compute_statistic(data: np.ndarray) -> dict:
    return {
        'mean' : np.mean(data),
        'stdev' : np.std(data, ddof=1),
        'max' : np.max(data),
        'min' : np.min(data),
        'median' : np.median(data),
        'q_95' : np.quantile(data, q=0.95),
        'q_05' : np.quantile(data, q=0.05),
    }

def compute_volume(maps: Mapping) -> dict:
    map = next(iter(maps.values()))
    return {'volume' : map.size}

def compute_statistics(tissues: Mapping) -> dict:
    statistics = {}
    for name, maps in tissues.items():
        statistics[name] = {
            map_name : compute_statistic(map)
            for map_name, map in maps.items()
        }
        statistics[name].update(compute_volume(maps))
    return statistics