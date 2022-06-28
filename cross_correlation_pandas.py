from scipy.signal import correlate
from scipy.signal import correlation_lags
from datetime import timedelta
import numpy as np

def cross_correlation_computation(x, y):
    

    
    
    #if len(x) < len(y):
    #    
    #    y = y.reindex(x.index)
    #if len(x) > len(y):
    #    x = x.reindex(y.index)

    x = x.interpolate()
    y = y.interpolate() 
        
    a = (x - x.mean()).values 
    b = (y - y.mean()).values
    
    #corre_cof = np.corrcoef(a,b)[0, 1]
    
    Z = np.argmax(correlate(a,b))
    lags = correlation_lags(a.size, b.size, mode="full")
    lag = lags[Z]
    print(f"Best lag: {str(timedelta(seconds=float(lag)))}")
    return lag