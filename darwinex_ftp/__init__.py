# -----------------------------------------------
# Libraries and packages
# -----------------------------------------------

import pandas as pd
from datetime import datetime
import os
from io import BytesIO
import gzip
import ftplib


# -----------------------------------------------
# Darwinex FTP functions
# -----------------------------------------------


class DarwinexFtp:
    """
    Creat a DarwinexFtp object to connect to the Darwinex FTP server and download files
    """

    def __init__(self, 
                 ftp_server, 
                 port, 
                 username, 
                 password
                 ):

        self.ftp_server = ftp_server
        self.username = username
        self.password = password
        self.port = port
        
        # Connect to the FTP server
        self.ftp = ftplib.FTP()
        self.ftp.connect(host=self.ftp_server, port=self.port)
        self.ftp.login(user=self.username, passwd=self.password)


    def get_ftp_files(self):
        """
        Return a list of folders/files in a given path in the ftp server
        """
        file_list = self.ftp.nlst()
        
        return file_list


    def download_darwin_dates(self, 
                              dict_YM, 
                              darwin='THA'
                              ):
        """
        Download the periods of available quotes data for a given asset (darwin), in a YYYY-MM format
        Arguments:
            - dict_YM: dictionary with the periods of available data for each asset
            - darwin: asset (darwin)
        Returns:
            - Dictionary with the periods of available data for each asset
        """
        ls_folders_darwin = self.ftp.nlst()
        print(ls_folders_darwin) if self.verbose >=3 else None
        dirname = f'quotes'

        if dirname in ls_folders_darwin:
            self.ftp.cwd(dirname=dirname)
            ls_folders_YM = self.ftp.nlst()
            print(ls_folders_YM) if self.verbose >=3 else None
            start_YM = min([datetime.strptime(YM, '%Y-%m') for YM in ls_folders_YM]).strftime('%Y-%m')
            end_YM = max([datetime.strptime(YM, '%Y-%m') for YM in ls_folders_YM]).strftime('%Y-%m')
            dict_YM[darwin][f'start{self.var}'] = start_YM
            dict_YM[darwin][f'end{self.var}'] = end_YM
            print(f'"{darwin}": ' + '{' + f'"start{self.var}": "{start_YM}", "end{self.var}": "{end_YM}"' + '},') if self.verbose >=1 else None
            self.ftp.cwd(dirname='..')        
        
        return dict_YM


    def get_darwins_dates(self, 
                          ls_assets=['THA'], 
                          verbose=0
                          ):
        """
        Get the periods of available quotes data for a list of assets (darwins), in a YYYY-MM format
        Arguments:
            - ls_assets: list of assets (darwins)
            - start_period: start period in YYYY-MM format
            - end_period: end period in YYYY-MM format
        Returns:
            - Pandas dataframe with the periods of available data for each asset. Columns:
                - start: start date of the data
                - end: end date of the data
                - start_var10: start date of the var10 data
                - end_var10: end date of the var10 data
            Remarks: "var10" dates indicates the former darwin data, when it was measured by var10 instead of VAR6.5. 
                     Please refer to the Darwinex documentation/support for more information.
        """
        self.verbose = verbose
        dict_YM = {}
        print(f'Checking darwins:') if self.verbose >=1 else None

        for darwin in ls_assets:

            dirname=darwin
            # check if dirname is a directory
            try:
                self.ftp.cwd(dirname=dirname)  # Navigate to the directory where the file is located
            except:
                print(f"{dirname} is a file")
                continue

            dict_YM[darwin] = {}

            self.var = ''
            dict_YM = self.download_darwin_dates(dict_YM, darwin)

            ls_folders_darwin = self.ftp.nlst()
            print(ls_folders_darwin) if verbose >=3 else None
            self.var = '_var10'
            dirname = f'_{darwin}_former{self.var}'
            if dirname in ls_folders_darwin:
                self.ftp.cwd(dirname=dirname)
                dict_YM = self.download_darwin_dates(dict_YM, darwin)
                self.ftp.cwd(dirname='..')
            self.ftp.cwd(dirname='..')

            columns = ['start', 'end', f'start{self.var}', f'end{self.var}']
            df_dates = pd.DataFrame.from_dict(dict_YM, orient='index', columns=columns)
            df_dates.index.name = 'darwin'

        return df_dates


    def fetch_file(self, 
                   file_name
                   ):
        """
        Download a file from the FTP server into a file object
        """
        self.fileobj = BytesIO()
        self.ftp.retrbinary(cmd=f'RETR {file_name}', callback=self.fileobj.write)
        self.fileobj.seek(0)

        return self.fileobj


    def unzip_file(self):
        """
        Unzip a file object and return data
        """
        data = gzip.GzipFile(fileobj=self.fileobj)

        return data


    def df_from_data(self):
        """
        Convert data into a pandas dataframe
        """
        df = pd.read_csv(self.data)
        df = df.set_index('timestamp', drop=True)
        df.index = pd.to_datetime(df.index, unit='ms')

        return df


    def download_quotes(self):
        """
        Download quotes data for a darwin from the FTP server.
        The function downloads data files existing in the YYYY-MM folders and returns a dataframe. Filters by start_period and end_period.
        Returns:
            - df_quotes: dataframe with quotes. Index are timestamps
        """
        dirname='quotes'
        self.ftp.cwd(dirname=dirname)
        print(self.ftp.nlst()) if self.verbose >=3 else None

        df_quotes_darwin = pd.DataFrame()

        ls_folders_YM = self.ftp.nlst()
        ls_folders_YM_filtered = [folder for folder in ls_folders_YM if (folder>=self.start_period) & (folder<=self.end_period)]

        for folder in ls_folders_YM_filtered:
            print(f'folder: {folder}') if self.verbose >=3 else None
            self.ftp.cwd(dirname=folder)
            print(self.ftp.nlst()) if self.verbose >=3 else None
            files = self.ftp.nlst()
            files = [file for file in files if file.endswith('.gz')]
            for file_name in files[:]:
                print(f'file: {file_name}') if self.verbose >=3 else None
                # Fetch the file and unzip it
                self.fileobj = self.fetch_file(file_name=file_name)
                self.data = self.unzip_file()
                df = self.df_from_data()
                df_quotes_darwin = pd.concat([df_quotes_darwin, df], axis=0)
            self.ftp.cwd(dirname='..')
        self.ftp.cwd(dirname='..')

        print(df_quotes_darwin) if self.verbose >=3 else None
        df_quotes_darwin.index = pd.to_datetime(df_quotes_darwin.index)
        df_quotes_darwin = df_quotes_darwin.sort_index()

        if self.resample is not None:
            df_quotes_darwin = df_quotes_darwin.resample(self.resample).last()
        
        return df_quotes_darwin


    def get_quotes(self, 
                   df_quotes, 
                   darwin='THA'
                   ):
        """
        Launch a download quotes function for a darwin and merges the darwin data with df_quotes
        Arguments:
            - df_quotes: dataframe with quotes
            - darwin: darwin to download
        Returns:
            - df_quotes: dataframe with quotes including the new darwin
        """
        dirname = f'quotes'
        if dirname in self.ftp.nlst():
            print(f'Downloading darwin: {darwin}{self.var}', end=' - ') if self.verbose >=1 else None
            df_quotes_darwin = self.download_quotes()
            df_quotes_darwin = df_quotes_darwin.rename(columns={'quote': f'{darwin}{self.var}'})
            try:
                df_quotes_cols = df_quotes.columns.to_list()
                df_quotes_darwin_cols = df_quotes_darwin.columns.to_list()
                common_cols = sorted(set(df_quotes_cols) & set(df_quotes_darwin_cols))
                common_cols.append('timestamp')
                df_quotes = pd.merge(df_quotes, df_quotes_darwin, how='outer', on=common_cols)
                print('Done') if self.verbose >=1 else None
            except ValueError:
                print(f'ValueError: {ValueError}')
                print(f'Error {dirname} for {darwin}{self.var}') if self.verbose >=1 else None
        else:
            print(f'No {dirname} for {darwin}{self.var}') if self.verbose >=1 else None

        return df_quotes


    def download_ftp_quotes_data(self, 
                                 ls_assets=['THA'], 
                                 include_var10=False, 
                                 start_period='2023-01', 
                                 end_period='2023-03', 
                                 resample='B', 
                                 path=None,
                                 verbose=True
                                 ):
        """
        Download Darwinex FTP quotes data for a list of assets (darwins) for a period of time. Filters by start_period and end_period.
        Arguments:
            - ls_assets: list of assets (darwins)
            - include_var10: include var10 data
            - start_period: start period in YYYY-MM format
            - end_period: end period in YYYY-MM format
            - resample: resample frequency (None by default). Useful to e.g. reduce data size if you just requires getting daily quotes
            - path: path to save df_quotes
            - verbose: print messages
        Returns:
            - df_quotes: dataframe with quotes for the list of assets (darwins)
        Remarks: "var10" dates indicates the former darwin data, when it was measured by var10 instead of VAR6.5. 
                 Please refer to the Darwinex documentation/support for more information.
        """
        self.start_period = start_period
        self.end_period = end_period
        self.resample = resample
        self.verbose = verbose

        # Load existing df_quotes
        if path is not None:
            try:
                file_name = 'quotes_data.pkl'
                file_path = path + os.sep + file_name
                df_quotes = pd.read_pickle(file_path)
                print(f'Existing df_quotes loaded from {path}') if verbose >=1 else None
                print(df_quotes) if verbose >=2 else None
            except:
                print(f'No df_quotes exists in {path}. A new one will be created') if verbose >=1 else None
                df_quotes = pd.DataFrame()
                df_quotes.index.name = 'timestamp'
        
        # Download data
        df_quotes = pd.DataFrame()
        df_quotes.index.name = 'timestamp'
        for darwin in ls_assets:
            # Navigate to the directory where the file is located
            dirname=darwin
            self.ftp.cwd(dirname=dirname)
            # List the files in the current directory
            print(self.ftp.nlst()) if self.verbose >=3 else None

            # Version var=6.5
            self.var = ''
            df_quotes = self.get_quotes(df_quotes=df_quotes, darwin=darwin)

            if include_var10:
                # Version var=10
                self.var = '_var10'
                dirname = f'_{darwin}_former{self.var}'  # Former DARWIN version var=10
                if dirname in self.ftp.nlst():
                    self.ftp.cwd(dirname=dirname)
                    print(self.ftp.nlst()) if self.verbose >=3 else None
                    df_quotes = self.get_quotes(df_quotes=df_quotes, darwin=darwin)
                    self.ftp.cwd(dirname='..')
                else:
                    print(f'No {dirname} for {darwin}') if self.verbose >=1 else None
            self.ftp.cwd(dirname='..')
            df_quotes = df_quotes.sort_index()

            # Save df_quotes
            if path is not None:
                df_quotes.to_pickle(file_path)
                print(f'df_quotes saved to {path}') if verbose >=3 else None

        return df_quotes


    def close_ftp_connection(self):
        """
        Closes the FTP connection
        """
        self.ftp.quit()


