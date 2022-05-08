def p_diff(obs,starttime,endtime, path_gsm):
    
        
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
    
    
    try:
        df_pillar = pd.read_csv(f'pillar_differences_{obs}.txt',sep = ' ')
    except:
        df_pillar = pd.DataFrame()
        
    for date in date_period:
        
        files_gsm.extend(glob.glob(f'{path_gsm}/{(datetime.strptime(str(date.date()),"""%Y-%m-%d""").strftime(""""%Y%m%d"""))[3::]}*'))
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
        
        
        
    for file_g,file_p,date in zip(files_gsm,files_ppm,days_with_files):
        
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

            
            print(f'***********************************')
            print(f'Calculating statistics for {Date}')
            mean = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]): str(df_gsm.index[-1])]).dropna().mean(), 2)
            means.append(mean)
            print(f'\n The mean differences was {mean} nT')
            median = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().mean(), 2)
            medians.append(median)
            print(f'\n The median was {median} nT')
            stds = round((df_gsm['F'] - df_ppm['F'].loc[str(df_gsm.index[0]):str(df_gsm.index[-1])]).dropna().std(),2)
            std.append(stds)
            print(f'\n The std was {stds} nT \n')
            #day = pd.to_datetime(Date,format= '%Y-%m-%d')
            days_index.append(Date)
            
        except:
            
            print(f'File {date} with problem')
            
            pass
            
    df_tpm['Date'] = days_index
    df_tpm['pillar_1_mean'] = means
    df_tpm['pillar_1_median'] = medians
    df_tpm['pillar_1_std'] = std
    
    if df_pillar.empty == True:
        
        df_tpm.set_index('Date', inplace = True)
        
        df_tpm.sort_index().to_csv(f'pillar_differences_{obs}.txt',
                                   sep = ' ')
        
        #plt.figure(figsize = (12, 4))
        #plt.plot(df_tpm['pillar_1_mean'], 'o', color = 'red', label = 'New measurements')
        #plt.legend()
        #plt.show()
        
    else:
        df_pillar = pd.concat([df_pillar, df_tpm], ignore_index = True)
        df_pillar.set_index('Date', inplace = True)
        df_pillar.drop_duplicates().sort_index().to_csv(f'pillar_differences_{obs}.txt', sep = ' ')
        
        #plt.figure(figsize = (12, 4))
        #plt.plot(df_pillar['pillar_1_mean'], 'o', color = 'blue')
        #plt.plot(df_tpm['pillar_1_mean'], 'o', color = 'red', label = 'New measurements')
        #plt.legend()
        #plt.show()
    
    return days_index,means,medians,std