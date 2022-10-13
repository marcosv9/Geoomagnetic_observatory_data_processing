from itertools import repeat
import pandas as pd
import numpy as np
from datetime import timedelta
from spacepy import pycdf
import chaosmagpy as cp




def time_shift_corre_coef_cdf(obs:str,
                              start_date: str,
                              end_date:str,
                              window_start: int,
                              window_end: int,
                              step: int = 1,
                              shift_direction: str = 'backward',
                              filetype: str = 'sec'
                             ):
    '''
    Write docstring
    
    Developed by Marcos Vinicius Silva
    
    Github: https://github.com/marcosv9
    
    '''
    obs = obs.upper()
    
    obs_list = ['MAA0', 'VSS0', 'VSS1',
                'VSS2', 'TTB0', 'TTB1']
    
    assert filetype in ['sec','ppm'], 'filetype must be sec or ppm'
    
    assert obs in obs_list, 'Invalid observatory code'
        
    assert shift_direction in ['backward', 'forward'], 'shift_direction must be forward or backward'    

    df_corr = pd.DataFrame()
    
    window_size = np.arange(window_start, window_end, step)
    
    if shift_direction == 'backward':
        time_signal = '-'
    else:
        time_signal = '+'
        
    #setting path to the files
    
    path = f'O:/jmat/{obs}/cdf'
        
    #creating an array with the days that will be investigated in the file date format    
    date_range_file_format = pd.date_range(start_date,
                                           end_date,
                                           freq = 'D').strftime('%Y%m%d')
        
    for date in date_range_file_format:
        try:
        
            data = pycdf.CDF(f'{path}/{obs}_{date}.cdf')
            
            df_cdf = pd.DataFrame()
            df_cdf['F_calc'] = np.sqrt((data['HNvar'][:] + data['H0'][1])**2 + (data['HEvar'][:])**2 + (data['Zvar'][:] + data['Z0'][1])**2 )
            df_cdf['Fsc'] = data['Fsc'][:]
            df_cdf['HNvar'] = data['HNvar'][:]
            df_cdf['Zvar'] = data['Zvar'][:]
            df_cdf['HEvar'] = data['HEvar'][:]
            # [Htot] used in TTB and MAA
            df_cdf['Htot'] = data['HNvar'][:] + data['H0'][1]
            df_cdf.index = pd.to_datetime(cp.data_utils.timestamp(data['time'][:]))
            data.close()
            
            #df_sec.index = pd.date_range(f'{date} {df_sec.index[0]}',f'{date} {df_sec.index[-1]}', freq = 's')
            
            #F_calc = np.sqrt((df_sec['X']**2 + df_sec['Z']**2))
            #df_sec['F_calc'] = F_calc
            
            df_coef = pd.DataFrame()
            coef_list = [[],[],[]]
            
            print(f'shifting the data to find the best adjust for {date}')
            
            #loop over the window_size to detect the best adjust in the selected window
            for i in window_size:
                
                #applying the shift direction, default is backwards
                if obs[0:3] in ['VSS']:
                    if shift_direction == 'backward':
                        coef = df_cdf['Fsc'].corr((df_cdf['F_calc']).shift(-i, 's'))
                    else:
                        coef = df_cdf['Fsc'].corr((df_cdf['F_calc']).shift(i, 's'))
                else:
                       
                    if shift_direction == 'backward':
                        coef = df_cdf['Fsc'].corr((df_cdf['Htot']).shift(-i, 's'))
                        
                    else:
                        coef = df_cdf['Fsc'].corr((df_cdf['Htot']).shift(i, 's'))
                        
                    
                coef_list[0].append(coef)
                coef_list[1].append(f'{time_signal}{str(timedelta(seconds=float(i)))}')
                coef_list[2].append(int(f'{time_signal}{i}'))
  
            #dataframe with the list of coefficients coefficients, shift_time and date
            df_coef['coef'] = coef_list[0]
            df_coef['Shift-Time (hh:mm:ss)'] = coef_list[1]
            df_coef['Date'] = date
            df_coef['Shift-Time (s)'] = coef_list[2]  
            df_coef['filetype'] = filetype
            
            #creating the output file with only the maximum correlation coefficient for each day
            
            df_corr = pd.concat([df_corr, df_coef.loc[df_coef['coef'] ==  df_coef['coef'].max()]])
            
        except:
            print(f'No CDF file found for {date}') 
                 
    return df_corr


if __name__ == '__main__':
    RMS = time_shift_corre_coef_cdf(obs = 'MAA0',
                                    start_date= '2021-09-01',
                                    end_date = '2021-09-18',
                                    window_start=35000,
                                    window_end=44000,
                                    step = 1,
                                    shift_direction = 'backward',
                                    filetype= 'sec'
                                    )
                                    #window_start=35000,
                                    #window_end=42000,
    print(RMS)
    