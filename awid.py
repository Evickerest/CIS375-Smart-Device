import pandas as pd
import numpy as np

data = pd.read_csv(
    "../Downloads/awid-csv/CSV/1.Deauth/Deauth_0.csv", 
    sep=",", 
    #error_bad_lines=False, 
    encoding='ISO-8859-1', 
    low_memory=False
)

print(data.shape)
        
data.replace("?", np.nan, inplace=True)
