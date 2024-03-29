import pandas as pd
import glob
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from spacepy import pycdf
import chaosmagpy as cp


def p_diff(obs: str,
           starttime: str,
           endtime: str,
           path_gsm: str,
           pillar:int = 1
           ):
    
    
    #list of days to check the existence of files    
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
    list_of_outlier = []
    
    
    # check the existence of previous pillars differences
    # if not exists a new one will be created.
    try:
        df_pillar = pd.read_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')
    except:
        df_pillar = pd.DataFrame(columns= [f'Date',
                                           f'p{pillar}_mean',
                                           f'p{pillar}_median',
                                           f'p{pillar}_std',
                                           f'jd'
                                           ]
                                 )
        df_pillar.to_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
  
   #cheking gsm files existence in the date period   
    
    for date in date_period:
        if obs.upper() in ['TTB0', 'TTB1']:
            
            files_gsm.extend(glob.glob(f'{path_gsm}/{(datetime.strptime(str(date.date()), """%Y-%m-%d""").strftime(""""%Y%m%d"""))[3::]}*'))
            files_gsm.sort()
            
        if obs.upper() in ['VSS0', 'VSS1']:
            
            files_gsm.extend(glob.glob(f'{path_gsm}/{date.date().strftime("""%Y%m%d""")}*'))
            files_gsm.sort()
    
   #creating list of dates only with gsm files existence.     
    for i in range(len(files_gsm)):
        
        if obs.upper() in ['TTB0', 'TTB1']:
            
            gsm_date = datetime.strptime(os.path.basename(files_gsm[i])[0:6], '%y%m%d').strftime('%Y%m%d')
            days_with_files.append(gsm_date)
            
        if obs.upper() in ['VSS0', 'VSS1']:
            gsm_date = datetime.strptime(os.path.basename(files_gsm[i])[0:8], '%Y%m%d').strftime('%Y%m%d')
            days_with_files.append(gsm_date)
    
    # cheking for ppm files in the days with gsm files.
    for i in days_with_files:
        files_ppm.extend(glob.glob(f'O:/jmat/{obs}/{obs}_{str(i)}.ppm'))
        files_ppm.sort()
    print(files_ppm)
    #creating list of dates only with ppm files existence.    
    for i in range(len(files_ppm)):
        
        ppm_date = os.path.basename(files_ppm[i])[5:13]
        
        real_days.append(ppm_date)

    #cheking if the days with gsm files are the same as the days with ppm files
    #if they are different then, ppm days will be considered.

    if len(real_days) != len(days_with_files):
        
        files_gsm = []
        days_with_files = real_days
        
        for date in days_with_files:
            if obs.upper() in ['TTB0', 'TTB1']:
                files_gsm.extend(glob.glob(f'{path_gsm}/{date[2::]}*'))
                files_gsm.sort()
            if obs.upper() in ['VSS0', 'VSS1']:
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
            
            if obs.upper() in ['TTB0', 'TTB1']:
                
                Time = pd.date_range(Date + ' ' + str(df_gsm.index[0]).zfill(8),
                                     Date + ' ' + str(df_gsm.index[-1]).zfill(8), 
                                     freq = '3s')
            if obs.upper() in ['VSS0', 'VSS1']:
                
                Time = pd.date_range(Date + ' ' + str(df_gsm.index[0]).zfill(8),
                                     Date + ' ' + str(df_gsm.index[-1]).zfill(8), 
                                     freq = '5s')                
            df_gsm.index = Time
            #df.pop('Time')

            #df_ppm = pd.read_csv(file_p,
            #                     header = None,
            #                     sep = '\s+',
            #                     usecols = [1, 2, 3],
            #                     names=['date', 'Time', 'F'],
            #                     parse_dates = {'Date': ['date', 'Time']},
            #                     index_col = 'Date')
            
            df_ppm = pd.DataFrame()
            data = pycdf.CDF(f'O:/jmat/{obs}/cdf/{obs}_{date}.cdf')
            #df_cdf['F_calc'] = np.sqrt((data['HNvar'][:] + data['H0'][1])**2 + (data['HEvar'][:])**2 + (data['Zvar'][:] + data['Z0'][1])**2 )
            df_ppm['Fsc'] = data['Fsc'][:]
            
            #df_cdf['HNvar'] = data['HNvar'][:]
            #df_cdf['Zvar'] = data['Zvar'][:]
            #df_cdf['HEvar'] = data['HEvar'][:]
            # [Htot] used in TTB and MAA
            #df_cdf['Htot'] = data['HNvar'][:] + data['H0'][1]
            df_ppm.index = pd.to_datetime(cp.data_utils.timestamp(data['time'][:]))
            data.close()
            
            df_ppm.loc[df_ppm['Fsc'] >= 99999.0, 'Fsc'] = np.nan
            df_ppm.loc[df_ppm['Fsc'] == 00000.00, 'Fsc'] = np.nan

            #calculating mean, median and standard deviation between the gsm and ppm files
            
            print(f'***********************************')
            print(f'Calculating statistics for {Date}')
            mean = round((df_gsm['F'] - df_ppm['Fsc'].loc[str(df_gsm.index[0]): str(df_gsm.index[-1])]).dropna().mean(), 2)
            
            print(f'\n The mean differences was {mean} nT')
            median = round((df_gsm['F'] - df_ppm['Fsc'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().median(), 2)
            
            print(f'\n The median was {median} nT')
            stds = round((df_gsm['F'] - df_ppm['Fsc'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().std(),2)
            
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
              
            df_pillar = pd.read_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')

            if df_pillar.empty == True:
                
                df_tpm.set_index('Date', inplace=True)
                df_tpm.sort_index().to_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
            else:
                
                df_pillar = pd.concat([df_pillar, df_tpm], ignore_index = True)
                df_pillar.set_index('Date', inplace = True)
                df_pillar = df_pillar[~df_pillar.index.duplicated(keep='last')]
                df_pillar.sort_index().to_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = ' ')
            
            
        except:
            
            files_with_problems.append(date)
            
            pass
    
        
    df_pillar = pd.read_csv(f'outputs/pillar_differences_{obs}_p{pillar}.txt', sep = '\s+')
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
    
    plt.savefig(f'outputs/pillar_differences_{obs}_p{pillar}.jpeg', dpi = 300)
    plt.show()
    
    if len(files_with_problems) > 0:
        
        print(f'****************************************************************'
              f'\nList of files with problems - GSM files\n')
        print(*files_with_problems, sep = '\n')
    
    return days_index, means, medians, std

def plot_pdiff(obs: str,
               pillar: str,
               starttime = None,
               endtime = None,
               lr_start = None,
               lr_end = None,
               plot_uncertainties:bool = False
               ):
    
    path = f'outputs/pillar_differences_{obs}_p{str(pillar)}.txt'
         
    df_obs = pd.read_csv(path, sep = '\s+', index_col= [0])

    df_obs.index = pd.to_datetime(df_obs.index, format = '%Y-%m-%d')
    
    if lr_start != None and lr_end != None:
        lr = True
        prediction, model = linear_regression(df_obs[lr_start:lr_end]['jd'],
                                              df_obs[lr_start:lr_end][f'p{pillar}_mean']
                                              )
    else:
        lr = False
    
    if starttime == None and endtime == None and lr == False:
        
        print('****************************************************************')
        print('Pillar differences statistics for the period')          
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'].std(),3))
    
        fig, ax = plt.subplots(figsize=(18,5)) 
        
        if plot_uncertainties == False:
            ax.plot(df_obs[f'p{pillar}_mean'], 'or',markersize = 5, label = f'p{pillar}_mean')
        else:
            ax.errorbar(df_obs.index, df_obs[f'p{pillar}_mean'], yerr=df_obs[f'p{pillar}_std'], fmt='.r', markersize = 10,label = f'p{pillar}_mean')
        
        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'].min(),0.95*df_obs[f'p{pillar}_mean'].max())
        ax.set_title(f'Pillar differences {obs.upper()}', fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
        
    
    if starttime == None and endtime == None and lr == True:
        
        print('****************************************************************')
        print('Pillar differences statistics for the period')
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'].std(),3))      
        print('****************************************************************')
        print('Linear Regression')
        print(f'y = {round(float(model.coef_),6)}x {round(float(model.intercept_),3)}')
        
        fig, ax = plt.subplots(figsize=(18,5)) 
        
        if plot_uncertainties == False:
            ax.plot(df_obs.index,
                    df_obs[f'p{pillar}_mean'],
                    'or',
                    markersize = 5,
                    label = f'p{pillar}_mean')
        else:
            ax.errorbar(df_obs.index,
                        df_obs[f'p{pillar}_mean'],
                        yerr=df_obs[f'p{pillar}_std'],
                        fmt='.r',
                        elinewidth=2,
                        markersize = 8,label = f'p{pillar}_mean')
        ax.plot(df_obs.loc[lr_start:lr_end].index,
                prediction,
                label = f'linear regression')

        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'].min(), 0.95*df_obs[f'p{pillar}_mean'].max())
        ax.set_title(f'Pillar differences {obs.upper()}', fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
          
    if starttime != None and endtime != None and lr == False:  
        
        print('****************************************************************')
        print('Pillar differences statistics for the period')          
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].std(),3))
      
        fig, ax = plt.subplots(figsize=(18,5)) 
        
        if plot_uncertainties == False:
            ax.plot(df_obs[f'p{pillar}_mean'][starttime:endtime], 'or',markersize = 5, label = f'p{pillar}_mean')
        else:
            ax.errorbar(df_obs[starttime:endtime].index,
                        df_obs[f'p{pillar}_mean'][starttime:endtime],
                        yerr=df_obs[f'p{pillar}_std'][starttime:endtime],
                        fmt='.r',
                        markersize = 5,
                        label = f'p{pillar}_mean')
        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'][starttime:endtime].min(),0.95*df_obs[f'p{pillar}_mean'][starttime:endtime].max())
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_title('Pillar differences ' + obs.upper(), fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
        
        
    if starttime != None and endtime != None and lr == True:
        
        print('****************************************************************')
        print('Pillar differences statistics for the period')        
        print('The maximum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].max(),3))
        print('The minimum difference is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].min(),3))
        print('The median:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].median(),3))
        print('The mean is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].mean(),3))
        print('The STD is:', round(df_obs[f'p{pillar}_mean'][starttime:endtime].std(),3))        
        print('****************************************************************')
        print('Linear Regression')
        print(f'y = {round(float(model.coef_),6)}x {round(float(model.intercept_),3)}')
        
        fig, ax = plt.subplots(figsize=(18,5)) 

        if plot_uncertainties == False:
            ax.plot(df_obs[starttime:endtime].index,
                    df_obs[f'p{pillar}_mean'][starttime:endtime],
                    'or',
                    markersize = 5,
                    label = f'p{pillar}_mean')
        else:
            ax.errorbar(df_obs[starttime:endtime].index,
                        df_obs[f'p{pillar}_mean'][starttime:endtime],
                        yerr=df_obs[f'p{pillar}_std'][starttime:endtime],
                        fmt='.r',
                        markersize = 5,
                        label = f'p{pillar}_mean')
        
        ax.plot(df_obs[lr_start:lr_end].index,
                prediction,
                label = f'Linear Regression')
        
        ax.set_ylabel('Differences(nT)', fontsize = 14)
        ax.set_ylim(1.05*df_obs[f'p{pillar}_mean'][starttime:endtime].min(),
                    0.95*df_obs[f'p{pillar}_mean'][starttime:endtime].max()
                    )
        ax.set_xlabel('Time', fontsize = 14)
        ax.set_title(f'Pillar differences {obs.upper()}', fontsize = 16)
        ax.grid()
        ax.legend(loc='best', fontsize = 12)
        plt.show()
              
           
        
    return df_obs


def jd2000(date):
    
    date = datetime.strptime(date, '%Y-%m-%d')
    return int((date - datetime(2000,1,1)).days)

def linear_regression(x, y):
    
    y = y.dropna()
    x = x.dropna()
    
    x = x.reindex(y.index)
    
    x_train = x.values.reshape(-1,1)
    y_train = y 
    
    model = LinearRegression()
    model.fit(x_train, y_train)
    
    prediction = model.predict(x_train)
    
    return prediction, model


if __name__ == '__main__':

#calculate pillar differences
    #p_diff(obs = 'TTB0',
    #       starttime = '2021-01-01',
    #       endtime = '2021-01-31',
    #       path_gsm = 'O:/jmat/gsmfiles/TTB/2021/Pilar 1',
    #       pillar = 1)

#plot pillar differences

    plot_pdiff(obs = 'TTB0',
               pillar = 1,
               starttime = None,
               endtime = None,
               lr_start = None,
               lr_end = None,
               plot_uncertainties = False
               )