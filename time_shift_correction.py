from read_ppm import read_ppm
from read_sec import read_sec
import pandas as pd
import numpy as np
import glob
import os 
from datetime import timedelta, datetime

def time_shift_correction(obs: str,
                          start_date: str,
                          end_date: str,
                          filetype: str = 'sec'):
    
    assert filetype in ['sec','ppm'], 'filetype must be sec or ppm'
    
    obs = obs.upper()
    
    obs_list = ['MAA0', 'VSS0', 'VSS1',
                'VSS2', 'TTB0', 'TTB1']
    
    assert obs in obs_list, 'Invalid observatory code'
        
    path = f'O:/jmat/{obs}/'
    
    files_path = []
    dates = []
    
    shift_data_path = f'outputs//{obs}_shift.txt'
    
    
    date_range_file_format = pd.date_range(start_date,
                                           end_date,
                                           freq = 'D').strftime('%Y%m%d')
    
    
    #loop over dates to store ppm and sec files path
    for date in date_range_file_format:
        
        path_to_file = f'{path}/{obs}_{date}.{filetype}'
        
        
        if os.path.exists(path_to_file) == True:
            
            files_path.append(path_to_file)
            dates.append(date)
                   
    #reading shift data file
    
    df_shift = pd.read_csv(shift_data_path,
                           sep = '\t',
                           index_col = 'Date'
                           )
         
    for date in dates:
        
        date_index_format = datetime.strptime(date, "%Y%m%d").strftime('%Y-%m-%d')
        
        if filetype == 'ppm': 
            df_obs = read_ppm(obs = obs,
                              date = date_index_format)
        else:
            df_obs = read_sec(obs = obs,
                              date = date_index_format)
        
        
        next_day = (datetime.strptime(date, "%Y%m%d") + timedelta(days=1)).date().strftime('%Y%m%d')
        
        previous_day = (datetime.strptime(date, "%Y%m%d") + timedelta(days=-1)).date().strftime('%Y%m%d')
        
        previous_day_index_format = (datetime.strptime(date, "%Y%m%d") + timedelta(days=-1)).date().strftime('%Y-%m-%d')
        
        next_day_index_format = (datetime.strptime(date, "%Y%m%d") + timedelta(days=1)).date().strftime('%Y-%m-%d')
        
        shitf_time = int(df_shift.loc[(df_shift.index == int(date)) & (df_shift['filetype'] == filetype)]['Shift-Time (s)'].values)
              
        if shitf_time <= 0:
            
            if os.path.exists(f'{path}{obs}_{next_day}.{filetype}') == True:
                
                if filetype == 'ppm': 
                    df_obs_2 = read_ppm(obs = obs,
                                        date = next_day_index_format)
                else:
                    df_obs_2 = read_sec(obs = obs,
                                        date = next_day_index_format)
        if shitf_time > 0:
            
            if filetype == 'ppm': 
                df_obs_2 = read_ppm(obs = obs,
                                    date = previous_day_index_format)
            else:
                df_obs_2 = read_sec(obs = obs,
                                    date = previous_day_index_format)
                    
        if df_obs_2.empty == False:    
            df = pd.concat([df_obs, df_obs_2])
        else:
            df = df_obs.copy()
            
        df = df.shift(shitf_time, freq = 's')
        
        if filetype == 'sec':
            df['time'].loc[date_index_format] = df.loc[date_index_format].index.time
        else:
            df['time1'].loc[date_index_format] = df.loc[date_index_format].index.time
            df['time2'].loc[date_index_format] = df.loc[date_index_format].index.time
            
        df.loc[date_index_format].to_csv(f'outputs/{obs}_{date}.{filetype}',
                                         header = None,
                                         index = False,
                                         sep = ' ',
                                         float_format="%.2f")    
                
if __name__ == '__main__':
    time_shift_correction(obs = 'MAA0',
                          start_date =  '2021-05-20',
                          end_date = '2021-05-20',
                          filetype = 'sec')        