import pandas as pd
from validate_date import validate

"""
Function to filter the kp-index since 1932

Inputs:

kp (float): must be between 0 and 9, the limit number
            to filter the kp-index.
            
start_date (str, format 'yyyy-mm-dd): the start date of the kp-index
                                      that will be filtered

end_date (str, format 'yyyy-mm-dd): the end date of the kp-index
                                      that will be filtered 
                                      
index_values (str, greater or smaller): set the direction of the filtering.
                                        If greater, will filter to values greater than
                                        the specified kp. If less, will filter to values
                                        smaller than the specified kp.
                                        
Outputs:

Pandas dataframe containing the filtered data

Saves a .txt file containing the filtered data    
    
   
"""

def kp_filter(kp:float,
              start_date:str,
              end_date:str,
              index_values:str = 'greater'
              ):
    
    #asserting inputs
    assert kp > 0 and  kp <= 9, 'kp must be between 0 and 9'
    
    assert index_values in ['greater', 'smaller'], 'index_values must be greater or smaller'
    
    for date in [start_date, end_date]:
        validate(date)
        
        
    # reading the most recent kp-index from gfz-website
    print('Loading the most recent kp-index from gfz-website...') 
    df_kp = pd.read_csv('https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt',
                      skiprows = 30,
                      header = None,
                      sep = '\s+', 
                      usecols = [0, 1, 2,
                                 3, 7, 8
                                 ],
                      parse_dates = {'Date': ['Y', 'M',
                                              'D','H'
                                              ]
                                     },
                      names = ['Y', 'M', 'D',
                               'H', 'Kp', 'Ap'
                               ],
                     )
    
    df_kp.index = pd.to_datetime(df_kp['Date'], format = '%Y %m %d %H.%f')
    df_kp.pop('Date') 
    
    if index_values == 'greater':
        df_kp.loc[df_kp['Kp'] > kp][start_date:end_date].to_csv(f'filtered_kp_index.txt',
                                                                sep = '\t')
    
        return df_kp.loc[df_kp['Kp'] > kp][start_date:end_date]
    else:
        df_kp.loc[df_kp['Kp'] < kp][start_date:end_date].to_csv(f'filtered_kp_index.txt',
                                                                sep = '\t')
        return df_kp.loc[df_kp['Kp'] < kp][start_date:end_date]


if __name__ == '__main__':
    kp = kp_filter(kp = 4,
              start_date = '2022-06-01',
              end_date = '2022-07-01',
              index_values = 'greater')
    print(kp)