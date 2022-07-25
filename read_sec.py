import pandas as pd
from datetime import datetime
from validate_date import validate
from itertools import repeat


def read_sec(obs:str,
             date: str):
    
    
    #validating inputs
    validate(date)
    
    obs = obs.upper()
    
    obs_list = ['MAA0', 'VSS0', 'VSS1',
                'VSS2', 'TTB0', 'TTB1']
    
    assert obs in obs_list, 'Invalid observatory code'
    
    date_file_format = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
          
    #setting path to the files
    
    file_path_sec = f'O:/jmat/{obs}/{obs}_{date_file_format}.sec'
    
    df_file = pd.read_csv(file_path_sec,
                          sep = '\s+',
                          names = ['time','X','Y','Z','T1','T2'])
    
    date_list = []
    date_list.extend(repeat(date,len(df_file)))
    
    df_file.index = pd.Series(date_list) + ' ' + df_file['time'] 
    
    df_file.index = pd.to_datetime(df_file.index, infer_datetime_format=True)
    
    return df_file


if __name__ == '__main__':
    df_file = read_sec(obs = 'VSS0',
                       date = '2021-04-01')