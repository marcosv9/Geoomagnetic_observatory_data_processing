import pandas as pd
from datetime import datetime
from validate_date import validate


def read_ppm(obs:str,
             date: str):
    
    
    validate(date)
    
    obs = obs.upper()
    
    obs_list = ['MAA0', 'VSS0', 'VSS1',
                'VSS2', 'TTB0', 'TTB1']
    
    assert obs in obs_list, 'Invalid observatory code'
    
    date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d")
        
    #setting path to the files

    file_path_ppm = f'O:/jmat/{obs}/{obs}_{date}.ppm'
    
    df_file = pd.read_csv(file_path_ppm,
                          sep = '\s+',
                          names = ['time1','date','time2','F','Q'])
    
    df_file.index = df_file['date'] + ' ' + df_file['time1'] 
    
    df_file.index = pd.to_datetime(df_file.index, infer_datetime_format=True)
    
    return df_file

if __name__ == '__main__':
    df_file = read_ppm(obs = 'VSS0',
             date = '2021-04-01')
    print(df_file)