from cmath import pi
from re import L
import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os


def p_diff(obs, starttime, endtime, path_gsm, pillar:int = 1):
    
        
    date_period = pd.date_range(starttime,endtime,freq = 'D')
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
    
    
    try:
        df_pillar = pd.read_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')
    except:
        df_pillar = pd.DataFrame(columns= [f'Date',
                                           f'p{pillar}_mean',
                                           f'p{pillar}_median',
                                           f'p{pillar}_std'
                                           ]
                                 )
        df_pillar.to_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
  
    for date in date_period:
        
        files_gsm.extend(glob.glob(f'{path_gsm}/{(datetime.strptime(str(date.date()), """%Y-%m-%d""").strftime(""""%Y%m%d"""))[3::]}*'))
        files_gsm.sort()
        
    for i in range(len(files_gsm)):
        
        f = datetime.strptime(os.path.basename(files_gsm[i])[0:6], '%y%m%d').strftime('%Y%m%d')
        days_with_files.append(f)

    for i in days_with_files:
        files_ppm.extend(glob.glob(f'O:/jmat/{obs}/{obs}_{str(i)}.ppm'))
        files_ppm.sort()
       
    for i in range(len(files_ppm)):
        
        f2 = os.path.basename(files_ppm[i])[5:13]
        real_days.append(f2)
    
    if len(real_days) != len(days_with_files):
        
        files_gsm = []
        days_with_files = real_days
        
        for date in days_with_files:
        
            files_gsm.extend(glob.glob(f'{path_gsm}/{date[2::]}*'))
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
                                 freq = '3s')
            df_gsm.index = Time
            #df.pop('Time')
            
            df_ppm = pd.read_csv(file_p,
                                 header = None,
                                 sep = '\s+',
                                 usecols = [1, 2, 3],
                                 names=['date', 'Time', 'F'],
                                 parse_dates = {'Date': ['date', 'Time']},
                                 index_col = 'Date')
            
            df_ppm.loc[df_ppm['F'] >= 99999.0, 'F'] = np.nan

            
            print(f'***********************************')
            print(f'Calculating statistics for {Date}')
            mean = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]): str(df_gsm.index[-1])]).dropna().mean(), 2)
            means.append(mean)
            print(f'\n The mean differences was {mean} nT')
            median = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().median(), 2)
            medians.append(median)
            print(f'\n The median was {median} nT')
            stds = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().std(),2)
            std.append(stds)
            print(f'\n The std was {stds} nT \n')
            #day = pd.to_datetime(Date,format= '%Y-%m-%d')
            days_index.append(Date)
            
            
            df_tpm[f'Date'] = [Date]
            df_tpm[f'p{pillar}_mean'] = [mean]
            df_tpm[f'p{pillar}_median'] = [median]
            df_tpm[f'p{pillar}_std'] = [stds]
                
            df_pillar = pd.read_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')

            if df_pillar.empty == True:
                
                df_tpm.set_index('Date', inplace=True)
                df_tpm.sort_index().to_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
            else:
                
                df_pillar = pd.concat([df_pillar, df_tpm], ignore_index = True)
                df_pillar.set_index('Date', inplace = True)
                df_pillar = df_pillar[~df_pillar.index.duplicated(keep='last')]
                df_pillar.sort_index().to_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
            
            
            
            #plt.figure(figsize = (12, 4))
            #plt.plot(df_pillar['pillar_1_mean'], 'o', color = 'blue')
            #plt.plot(df_tpm['pillar_1_mean'], 'o', color = 'red', label = 'New measurements')
            #plt.legend()
            #plt.show()
                     
            
        except:
            
            files_with_problems.append(date)
            
            pass
    
        
    df_pillar = pd.read_csv(f'pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')
    df_pillar.set_index('Date',inplace = True)
    df_pillar.index = pd.to_datetime(df_pillar.index, format = '%Y-%m-%d')
    
    days_index = pd.to_datetime(days_index, format = '%Y-%m-%d')
    
    plt.figure(figsize=(12,4))
    plt.title(f'Pillar Differences {obs} Pillar {pillar}')
    plt.xlabel('Date')
    plt.ylabel(f'F_var - F_p{pillar} (nT)')
    plt.plot(df_pillar[f'p{pillar}_mean'], 'o', color = 'blue')
    plt.plot(days_index, means, 'o', color = 'red', label = 'New measurements')
    plt.legend()
    
    plt.savefig(f'pillar_differences_{obs}_p{pillar}.png', dpi = 300)
    plt.show()
    
    print(f'****************************************************************'
          f'\nList of files with problems - GSM files\n')
    print(*files_with_problems, sep = '\n')   
    
    return days_index,means,medians,std

def plot_pdiff(obs, pillar,  starttime = None, endtime = None):
    
    path = f'pillar_differences_{obs}_p{pillar}.txt'
         
    df_obs = pd.read_csv(path, sep = '\s+', index_col= [0])

    df_obs.index = pd.to_datetime(df_obs.index, format = '%Y-%m-%d')
    
    
    if starttime == None and endtime == None:
    
        fig, ax = plt.subplots(figsize=(18,5)) 
    #gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    #Days = ['01/01','03/01','05/01','07/01','09/01','11/01']
    #ax0 = plt.subplot(gs[0])
        ax.plot(df_obs[f'p{pillar}_mean'], 'or',markersize = 5, label = f'p{pillar}_mean')
#ax.plot(df1['jd'],pl(df1['jd']),'k--',label = 'linear trend = 0.002429x - 50.53', markersize = 4)
#ax[0].plot(df2['doy'], df2['over'] , 'o--',label = 'GSM Over',markersize = 5)
#ax[0].plot(DOY,pl(DOY),'r-',label = 'trend')
#ax[0].set_xticklabels(Days)
#ax.set_ylim(-35,-28)
#ax[0].set_xticks(np.arange(0,365,61))
#ax[0].axhline(y=np.mean(Diff), c='k', linewidth=2, alpha=0.5, linestyle='--',label = 'mean =-32,21 nT')
#ax.set_xlim(7252,7669)
        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'].min(),0.95*df_obs[f'p{pillar}_mean'].max())
        ax.set_title(f'Pillar differences {obs.upper()}', fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
        
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'].std(),3))
        
    else:
        fig, ax = plt.subplots(figsize=(18,5)) 
    #gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1]) 
    #Days = ['01/01','03/01','05/01','07/01','09/01','11/01']
    #ax0 = plt.subplot(gs[0])
        ax.plot(df_obs[f'p{pillar}_mean'][starttime:endtime], 'or',markersize = 5, label = f'p{pillar}_mean')
#ax.plot(df1['jd'],pl(df1['jd']),'k--',label = 'linear trend = 0.002429x - 50.53', markersize = 4)
#ax[0].plot(df2['doy'], df2['over'] , 'o--',label = 'GSM Over',markersize = 5)
#ax[0].plot(DOY,pl(DOY),'r-',label = 'trend')
#ax[0].set_xticklabels(Days)
#ax.set_ylim(-35,-28)
#ax[0].set_xticks(np.arange(0,365,61))
#ax[0].axhline(y=np.mean(Diff), c='k', linewidth=2, alpha=0.5, linestyle='--',label = 'mean =-32,21 nT')
#ax.set_xlim(7252,7669)
        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'][starttime:endtime].min(),0.95*df_obs[f'p{pillar}_mean'][starttime:endtime].max())
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_title('Pillar differences ' + obs.upper(), fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
        
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].std(),3))

