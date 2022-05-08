import pandas as pd
from glob import glob
import pathlib
from datetime import datetime
import ftplib
import os
from datetime import datetime

def download_GFZ_ftp(starttime, endtime , obs):
    '''
    Function to automatize the data download of the Brazilian
    geomagnetic observatories and stations from the GFZ-potsdam
    ftp server.

    **************************************************************
    Args:

       starttime (str) - First date of to be download, format = 'YYYY-MM-DD'

       endtime (str) - Last date of to be download, format = 'YYYY-MM-DD'

       obs (str, list or None) = observatory os interest or list of .
                 *if None, the data will be downloaded 
                  for all of the geomagnetic observatories 
                  and stations

    *******************************************************************
    Usage example: 
        download_GFZ_ftp_files(starttime = '2022-04-02',
                               endtime = '2022-04-10' ,
                               obs = ['TTB0','TTB1'])

    '''
    
    #checking input formats
    for i in [starttime, endtime]:
        validate(i)

    files_date = []

    #connecting to the ftp server

    ftp = ftplib.FTP(f'ftp_server')
    ftp.login('anonymous', 'email@email.com')

    print(f'Connected to ftp server')
    
    #creating the date range for the specified period
    
    date_period = pd.date_range(starttime, endtime, freq = 'D')

    #setting the stations that will be used
    
    if obs not in ['TTB0', 'TTB1', 'VSS0',
                  'VSS1', 'VSS2', 'MAA0'
                  ]:
        raise ValueError('Type a valid observatory or station!')



    if obs == None:

        obs = ['TTB0', 'TTB1', 'VSS0',
               'VSS1', 'VSS2', 'MAA0'
              ]

    if obs == 'TTB':

        obs = ['TTB0','TTB1']

    if obs == 'VSS':

        obs = ['VSS0','VSS1','VSS2']

    if obs == 'MAA':

        obs = ['MAA0']    

    else:
        obs = obs
    
    # loop over the stations to get the files for each one

    for station in obs:
        
        #setting the output directory
        directory_output = f'O:/jmat/{station.upper()}'

        #setting the ftp path 
        path_secppm = f'/pub/home/obs/data/relative/second/jmat/{station.upper()}'
    
        #changing the ftp directory
        ftp.cwd(path_secppm)
        files_date = []
        for date in date_period:           

            f =  datetime.strptime(str(date.date()), "%Y-%m-%d").strftime("%Y%m%d")
            files_date.append(f)      
        
        
        pathlib.Path(directory_output).mkdir(parents=True, exist_ok=True)
        for file in files_date:

            #listing the files in the ftp server
            try:    
                filenames = ftp.nlst(f'{station.upper()}_{file}*')
                for filename in filenames:
                    # downloading file and saving the correct directory
                    local_filename = os.path.join(directory_output, filename)
                    file = open(local_filename, 'wb')
                    ftp.retrbinary(f'RETR {filename}', file.write)
                    print(f'File {filename} downloaded!')
                
                    
            except:
                print(f'No file in {file} to download for {station.upper()}.')
                pass              
            
    ftp.quit()
    print('Disconnected from Ftp server!')  


def validate(str_date):
    try:
        datetime.strptime(str_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError('Incorrect date format, should be YYYY-MM-DD')