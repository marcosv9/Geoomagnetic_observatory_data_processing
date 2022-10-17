from email.utils import parsedate_to_datetime
import pandas as pd
import urllib.request
import requests
import datetime
import numpy as np
from pandas.tseries.frequencies import to_offset
from calendar import monthrange
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import os


def get_realtime_dst(starttime,
                     endtime,
                     save_files:bool = False,
                     save_plots:bool = False):
    
    
    working_directory = os.getcwd()
    
    #dates = pd.date_range(np.datetime64(starttime),
    #                      np.datetime64(endtime) +1,
    #                      freq = 'M')
    
    today = datetime.datetime.today()
    
    datem = datetime.datetime(today.year, today.month, 1)
    
    df_final = pd.DataFrame()
    
    df_definitive = pd.read_html('https://wdc.kugi.kyoto-u.ac.jp/dst_final/index.html')
    
    #df_provisional = pd.read_html('https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/index.html')
    
    df_current = pd.read_html('https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/index.html')
    
    dates_checked = check_dst_in_database(starttime,
                                  endtime)

    dates = []
    for i in dates_checked:
        dates += [pd.to_datetime(i)]
        
    
    if len(dates) != 0:    
        for date in dates:
        
            if int(date.year) <= int(df_definitive[0].Year.values[-1]):
                
                datatype = 'F'
                html = f'https://wdc.kugi.kyoto-u.ac.jp/dst_final/{date.year}{str(date.month).zfill(2)}/index.html'   
                url = requests.get(html).text
                print(html)
                
            elif int(date.year) > int(df_definitive[0].Year.values[-1]) and int(date.year) < int(df_current[0].Year.values[0]):
                
                datatype = 'P'
                html = f'https://wdc.kugi.kyoto-u.ac.jp/dst_provisional/{date.year}{str(date.month).zfill(2)}/index.html'   
                url = requests.get(html).text
                #print(html)
                
            else:
                datatype = 'RT'
                html = f'https://wdc.kugi.kyoto-u.ac.jp/dst_realtime/{date.year}{str(date.month).zfill(2)}/index.html'   
                url = requests.get(html).text
                #print(html)                
                
        
            soup = BeautifulSoup(url, "html.parser")
            #soup = BeautifulSoup(url,"lxml")
            data = soup.find('pre', class_='data').get_text()
            days_in_month = monthrange(date.year, date.month)[1]
            
            with open(r'dst_'+ str(date.year) + '_' + str(date.month).zfill(2) + '_realtime.txt', 'w') as fp:
                for item in data:
            # write each item on a new line
                    fp.write(item)
                    
            if datetime.datetime(date.year,date.month,date.day) > datem:
                
                today = datetime.datetime.today().date()
                days_in_month = monthrange(today.year, today.month)[1]
                
                df = pd.read_csv(f'dst_{today.year}_{today.month}_realtime.txt',
                             skiprows = 8,
                             header = None,
                             sep = '\s+',
                             index_col = [0],
                             dtype = str)
                 
                df.index = pd.date_range(f'{today.year}-{today.month}',
                                         f'{today.year}-{today.month}-{days_in_month}',
                                         freq = 'D'
                                         )
                
                df = df.replace('99999999999999999999999999999999',
                                np.nan)
                
                #today = pd.to_datetime(datetime.datetime.today().date(), format = '%Y-%m-%d')
                df = df.replace(df.loc[str(today)][df.loc[str(today)].last_valid_index()], np.nan)
                    
                for col in df.columns:
                    df[col] = pd.to_numeric(df[col])
                    
                daily_index = []
                values = []
                for i,j in zip(df.index, range(len(df.index))):
                    values.extend(df.iloc[j].values)
                    for col in df.columns:
                        daily_index.append(i + to_offset(f'{df[col].name}H'))
                        
                df_dst_current = pd.DataFrame()
                df_dst_current.index = daily_index
                df_dst_current.index.name = 'Date'
                df_dst_current['Values'] = values
                df_dst_current['datatype'] = datatype
                df_dst_current = df_dst_current.shift(-1, freq = 'H')
                              
            else:
                        
                pd.read_csv(f'dst_{date.year}_{str(date.month).zfill(2)}_realtime.txt',
                            skiprows = 8,
                            header = None,
                            sep = ',').to_csv(f'dst_{date.year}_{str(date.month).zfill(2)}_realtime.txt',
                                              sep = '\t',
                                              header = None,
                                              index = False)
                
                with open(f'dst_{date.year}_{str(date.month).zfill(2)}_realtime.txt') as f:
                    lines = f.readlines()
                 
                n = 4
                comp_day = []
                for line in range(len(lines)):
                    lines[line] = lines[line][3:35] + lines[line][36:68] + lines[line][69:101]
                    
                    comp_day += [lines[line][i:i+n] for i in range(0, len(lines[line]), n)] 
                    
                    
                time_index = pd.date_range(f'{date.year}-{date.month}',
                                         f'{date.year}-{date.month}-{days_in_month} 23:00:00',
                                         freq = 'H'
                                         )
                df_dst = pd.DataFrame(index = time_index, data = comp_day)   
                 
                #df = df.replace('99999999999999999999999999999999',
                #                np.nan)
                
                #date = pd.to_datetime(datetime.datetime.date().date(), format = '%Y-%m-%d')
                #df = df.replace(df.loc[str(date)][df.loc[str(date)].last_valid_index()], np.nan)
                    
                #for col in df.columns:
                #    df[col] = pd.to_numeric(df[col])
                df_dst[0] = pd.to_numeric(df_dst[0])    
                #index_list = []
                #values = []
                #for i,j in zip(df.index, range(len(df.index))):
                #    values.extend(df.iloc[j].values)
                #    for col in df.columns:
                #        index_list.append(i + to_offset(f'{df[col].name}H'))
                        
                #df_dst = pd.DataFrame()
                #df_dst.index = index_list
                df_dst.index.name = 'Date'
                df_dst = df_dst.rename(columns = {0: 'Values'})
                df_dst['datatype'] = datatype
                #df_dst = df_dst.shift(-1, freq = 'H')
                
                df_final = pd.concat([df_final, df_dst])
                
        if datetime.datetime(date.year, date.month, date.day) > datem:
            
            df_final = pd.concat([df_final, df_dst_current.dropna()])
            
        #creating list of years without files and no duplicates
        years = []
        for i in dates:
            years += [i.year]
            
        years = list(set(years))       
        for year in years:
            
            if os.path.isfile(os.path.join(working_directory,
                                           'dst_yearly_files',
                                           f'dst_{year}.txt')) == True:
            
                df = pd.read_csv(os.path.join(working_directory,
                                              'dst_yearly_files',
                                              f'dst_{str(year)}.txt'
                                              ),
                                 sep = '\t',
                                 index_col= [0]
                                 )
                df.index = pd.to_datetime(df.index, format = '%Y-%m-%d %H:%M:%S')
            
                df_final = pd.concat([df, df_final]).sort_index()
                df_final = df_final[~df_final.index.duplicated(keep='first')]
                
            df_final.loc[str(year)].to_csv(os.path.join(f'dst_yearly_files',
                                                        f'dst_{year}.txt'),
                                                        sep = '\t',
                                                        encoding='ascii')
        
        for date in dates:
            
            os.remove(f'dst_{date.year}_{str(date.month).zfill(2)}_realtime.txt')
    else:
        dates = pd.date_range(str(starttime),
                              str(endtime),
                              freq = 'M'
                              )
        for year in dates.year.drop_duplicates():
            
            df = pd.read_csv(os.path.join(working_directory,
                                          'dst_yearly_files',
                                          f'dst_{str(year)}.txt'
                                          ),
                             sep = '\t',
                             index_col= [0]
                             )
            df.index = pd.to_datetime(df.index, format = '%Y-%m-%d %H:%M:%S')
            
            df_final = pd.concat([df, df_final]).sort_index()
            df_final = df_final[~df_final.index.duplicated(keep='first')]
                 
        
    return df_final.loc[starttime:endtime]

def check_dst_in_database(starttime,
                          endtime):
    
    working_directory = os.getcwd()
    
    years_without_files = []
    
    time_interval = pd.date_range(starttime,
                                  f'{endtime} 23:00:00' ,
                                  freq = 'H')
    df_dst = pd.DataFrame()
    
    for years in time_interval.year.drop_duplicates():
        
        if os.path.isfile(os.path.join(working_directory,
                                       'dst_yearly_files',
                                       f'dst_{years}.txt')) == True:
            
            df = pd.read_csv(os.path.join(working_directory,
                                          'dst_yearly_files',f'dst_{str(years)}.txt'
                                          ),
                             sep = '\t',
                             index_col= [0]
                             )
            df.index = pd.to_datetime(df.index, format = '%Y-%m-%d %H:%M:%S')
            
            df_dst = pd.concat([df_dst, df])
        else:
            years_without_files + [years]
            dates_without_files = []
            for year in years_without_files:
                for month in range(1,13):
                    dates_without_files += [f'{year}-{str(month).zfill(2)}'] 
            
    #dates_not_in_database = []
    missing_date = []
    if not df_dst.empty:  
        for date in time_interval:
            #print(date)     
            if date not in df_dst.index:
                #dates_not_in_database += [str(date)]
                missing_date += [f'{str(date.year).zfill(2)}-{str(date.month).zfill(2)}']
                missing_date = list(set(missing_date))
        missing_date += years_without_files
    else:
        missing_date == years_without_files
    missing_date.sort()
            
    #df_dst = df_dst.resample('M').mean()
        
    return missing_date 
   
    
        
    
    
if __name__ == '__main__':
    
    df = get_realtime_dst(starttime= '2015-01-01',
                          endtime = '2022-10-15')
    
    #dates = check_dst_in_database(starttime = '2022-10-01',
    #                           endtime = '2022-10-30')
    #
    print(df)