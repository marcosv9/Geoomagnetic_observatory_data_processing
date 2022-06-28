import pandas as pd
import numpy as np
import os
from datetime import timedelta



def time_shift_corre_coef(obs:str,
                          start_date: str,
                          end_date:str,
                          window_start: int,
                          window_end: int,
                          step: int = 1,
                          shift_direction: str = 'backward'
                         ):
    
    obs = obs.upper()
    if obs not in ['MAA0', 'TTB0']:
        print(f'obs must be MAA or TTB')
        
    if shift_direction not in ['backward', 'forward']:
        print(f'shift_direction must be forward or backward')    
        
    files_sec = []
    files_ppm = []
    dates_ppm = []
    dates_sec = []
    df_corr = pd.DataFrame()
    window_size = np.arange(window_start, window_end, step)
        
    #setting path to the files
    
    path = f'O:/jmat/{obs}'
        
    #creating an array with the days that will be investigated in the file date format    
    date_range_file_format = pd.date_range(start_date,
                                           end_date,
                                           freq = 'D').strftime('%Y%m%d')
    
    #creating an array with the days that will be investigated
    date_range = pd.date_range(start_date,
                               end_date,
                               freq = 'D')
    
    #loop over dates to store ppm and sec files path
    for date in date_range_file_format:
        
        file_path_ppm = f'{path}/{obs}_{date}.ppm'
        file_path_sec = f'{path}/{obs}_{date}.sec'
        
        if os.path.exists(file_path_ppm) == True:
            
            files_ppm.append(file_path_ppm)
            dates_ppm.append(date)
            
        if os.path.exists(file_path_sec) == True:
            
            dates_sec.append(date)
            files_sec.append(file_path_sec)

    if dates_ppm != dates_sec:
        
        days_with_both_files = list(set(dates_ppm).intersection(dates_sec))
        
        #checking if there is at least one day with both files
        if days_with_both_files == []:
            print('No data to check')
        else:
            #converting days_with_both_files to a int list and sorting it
            new_list = [int(i) for i in days_with_both_files]
            new_list.sort()
        
            days_with_both_files = new_list

    else:
        days_with_both_files = dates_ppm
        
    for date in days_with_both_files:
        
        #creating a dataframe for the ppm file in the date
        df_ppm = pd.read_csv(f'{path}/{obs}_{date}.ppm',
                             header = None,
                             skiprows = 0,
                             sep = '\s+',
                             parse_dates = {'Date': ['date', 'time']},
                             usecols = [1, 2, 3],
                             names = ['date', 'time', 'F'],
                             index_col = 'Date')
        df_ppm.loc[df_ppm['F'] >= 99999.0, 'F'] = np.nan
        df_ppm.loc[df_ppm['F'] == 00000.00, 'F'] = np.nan
        
        #creating a dataframe for the sec file in the date
        df_sec = pd.read_csv(f'{path}/{obs}_{date}.sec',
                     header = None,
                     skiprows = 0,
                     sep = '\s+',
                     usecols = [0, 1, 2, 3],
                     names = ['time', 'X', 'Y', 'Z'],
                     index_col = 'time')
        df_sec.loc[df_sec['X'] >= 99999.0, 'X'] = np.nan
        df_sec.loc[df_sec['Y'] >= 99999.0, 'Y'] = np.nan
        df_sec.loc[df_sec['Z'] >= 99999.0, 'Z'] = np.nan
        
        df_sec.index = pd.date_range(f'{date} {df_sec.index[0]}',f'{date} {df_sec.index[-1]}', freq = 's')
        
        #F_calc = np.sqrt((df_sec['X']**2 + df_sec['Z']**2))
        #df_sec['F_calc'] = F_calc
        
        df_coef = pd.DataFrame()
        coef_list = [[],[]]
        
        print(f'shifting the data to find the best adjust for {date}')
        
        #loop over the window_size to detect the best adjust in the selected window
        for i in window_size:
            
            #applying the shift direction, default is backwards
            if shift_direction == 'backward':
                coef = df_ppm['F'].corr(df_sec['X'].shift(-i, 's'))
            else:
                coef = df_ppm['F'].corr(df_sec['X'].shift(i, 's'))
                
            coef_list[0].append(coef)
            coef_list[1].append(str(timedelta(seconds=float(i))))
            
        #dataframe with the list of coefficients coefficients, shift_time and date
        df_coef['coef'] = coef_list[0]
        df_coef['Shift-Time'] = coef_list[1]
        df_coef['Date'] = date
        
        #creating the output file with only the maximum correlation coefficient for each day
        df_corr = pd.concat([df_corr,df_coef.loc[df_coef['coef'] ==  df_coef['coef'].max()]])
        
    return df_corr


if __name__ == '__main__':
    RMS = time_shift_corre_coef(obs = 'MAA0',
                   start_date= '2021-05-01',
                   end_date = '2021-05-15',
                   window_start=14000,
                   window_end=18000,
                   step = 1,
                   shift_direction = 'backward'
                  )