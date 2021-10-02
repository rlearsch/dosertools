import pandas as pd
import numpy as np

def closest_index_for_value(dataset : pd.DataFrame,column : str,value : float) -> int:
    closest_index = np.abs(dataset[column]-value).idxmin(axis=0)
    return closest_index
