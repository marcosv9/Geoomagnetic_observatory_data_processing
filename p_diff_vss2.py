import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from spacepy import pycdf
import chaosmagpy as cp

def p_diff_vss2(starttime, endtime, path_gsm, pillar):
    
    date_period = pd.date_range(starttime,
                                endtime,
                                freq = 'D'
                                )
    
    days_with_files = []
    real_days = []
    files_ppm = []
    files_gsm = []
    means = []
    medians = []
    std = []
    df_tpm = pd.DataFrame()
    days_index = []
    files_with_problems = []
    
        # check the existence of previous pillars differences
    # if not exists a new one will be created.
    try:
        df_pillar = pd.read_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = '\s+')
    except:
        df_pillar = pd.DataFrame(columns= [f'Date',
                                           f'p{pillar}_mean',
                                           f'p{pillar}_median',
                                           f'p{pillar}_std',
                                           f'jd'
                                           ]
                                 )
        df_pillar.to_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = ' ')
        
        
    for date in date_period:
        
        files_gsm.extend(glob.glob(f'{path_gsm}/{date.date().strftime("""%Y%m%d""")}*'))
        files_gsm.sort()
        
       #creating list of dates only with gsm files existence.     
    for i in range(len(files_gsm)):

        gsm_date = datetime.strptime(os.path.basename(files_gsm[i])[0:8], '%Y%m%d').strftime('%Y%m%d')
        days_with_files.append(gsm_date)   
           
        # cheking for ppm files in the days with gsm files.
        
    for i in days_with_files:
        if os.path.exists(f'O:/jmat/VSS2/cdf/VSS2_{str(i)}.cdf') == True:
             
            files_ppm.extend(glob.glob(f'O:/jmat/VSS2/cdf/VSS2_{str(i)}.cdf'))
            files_ppm.sort()
            real_days.append(i)
            
    if len(real_days) != len(days_with_files):
            
        files_gsm = []
        days_with_files = real_days
        for date in days_with_files:
            files_gsm.extend(glob.glob(f'{path_gsm}/{date}*'))
            files_gsm.sort() 
        
    for file_g, file_p, date in zip(files_gsm, files_ppm, days_with_files):
    
        try:
            df_gsm = pd.read_csv(file_g,
                                 header = None,
                                 skiprows = 10,
                                 sep = '\s+',
                                 usecols = [0, 1],
                                 names = ['time', 'F'],
                                 index_col = 'time')
        
            Date = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
            
                
            Time = pd.date_range(Date + ' ' + str(df_gsm.index[0]).zfill(8),
                                     Date + ' ' + str(df_gsm.index[-1]).zfill(8), 
                                     freq = '5s')                
            df_gsm.index = Time
            #df.pop('Time')
            
            
            data = pycdf.CDF(f'O:/jmat/VSS2/cdf/VSS2_{date}.cdf')
            
            df_ppm = pd.DataFrame()
            df_ppm['F_calc'] = np.sqrt((data['HNvar'][:] + data['H0'][1])**2 + (data['HEvar'][:])**2 + (data['Zvar'][:] + data['Z0'][1])**2 )
            # [Htot] used in TTB and MAA
            df_ppm.index = pd.to_datetime(cp.data_utils.timestamp(data['time'][:]))
            data.close()

            
            df_ppm.loc[df_ppm['F_calc'] >= 99999.0, 'F_calc'] = np.nan
            df_ppm.loc[df_ppm['F_calc'] == 00000.00, 'F_calc'] = np.nan
            
            #calculating mean, median and standard deviation between the gsm and ppm files
            
            print(f'***********************************')
            print(f'Calculating statistics for {Date}')
            mean = round((df_gsm['F'] - df_ppm['F_calc'].loc[str(df_gsm.index[0]): str(df_gsm.index[-1])]).dropna().mean(), 2)
            
            print(f'\n The mean differences was {mean} nT')
            median = round((df_gsm['F'] - df_ppm['F_calc'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().median(), 2)
            
            print(f'\n The median was {median} nT')
            stds = round((df_gsm['F'] - df_ppm['F_calc'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().std(),2)
            
            print(f'\n The std was {stds} nT \n')
            #day = pd.to_datetime(Date,format= '%Y-%m-%d')
                
            means.append(mean)
            medians.append(median)
            std.append(stds)
            days_index.append(Date)
            jd = jd2000(Date)
                
            df_tpm[f'Date'] = [Date]
            df_tpm[f'p{pillar}_mean'] = [mean]
            df_tpm[f'p{pillar}_median'] = [median]
            df_tpm[f'p{pillar}_std'] = [stds]
            df_tpm[f'jd'] = [jd]
            
            df_pillar = pd.read_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = '\s+')

            if df_pillar.empty == True:
                
                df_tpm.set_index('Date', inplace=True)
                df_tpm.sort_index().to_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = ' ')
            else:
                
                df_pillar = pd.concat([df_pillar, df_tpm], ignore_index = True)
                df_pillar.set_index('Date', inplace = True)
                df_pillar = df_pillar[~df_pillar.index.duplicated(keep='last')]
                df_pillar.sort_index().to_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = ' ')
            
            
        except:
            
            files_with_problems.append(date)
            
            pass
    
        
    df_pillar = pd.read_csv(f'outputs/pillar_differences_VSS2_p{pillar}.txt', sep = '\s+')
    df_pillar.set_index('Date',inplace = True)
    df_pillar.index = pd.to_datetime(df_pillar.index, format = '%Y-%m-%d')
    
    days_index = pd.to_datetime(days_index, format = '%Y-%m-%d')
    
    plt.figure(figsize=(12,4))
    plt.title(f'Pillar Differences VSS2 Pillar {pillar}')
    plt.xlabel('Date')
    plt.ylabel(f'F_var - F_p{pillar} (nT)')
    plt.plot(df_pillar[f'p{pillar}_mean'], 'o', color = 'blue')
    plt.plot(days_index, means, 'o', color = 'red', label = 'New measurements')
    plt.legend()
    
    plt.savefig(f'outputs/pillar_differences_VSS2_p{pillar}.jpeg', dpi = 300)
    plt.show()
    
    if len(files_with_problems) > 0:
        
        print(f'****************************************************************'
              f'\nList of files with problems - GSM files\n')
        print(*files_with_problems, sep = '\n')
    
    return days_index, means, medians, std            
            
            
def jd2000(date):
    
    date = datetime.strptime(date, '%Y-%m-%d')
    return int((date - datetime(2000,1,1)).days)

        
if __name__ == '__main__':
    p_diff_vss2(starttime = '2020-01-01',endtime = '2020-12-31', path_gsm='O:/jmat/gsmfiles/VSS/2020', pillar = 1)