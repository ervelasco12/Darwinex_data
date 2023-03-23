# darwinex-data

This is a Python package to download historical quotes data of Darwinex darwins. It gets the data available on the Darwinex FTP server, in resolution of a second. 
Quotes data are returned as a Pandas dataframe, and can be stored as a pickle.
Other types of darwin data are available at the FTP server, including time series and statistics which support the data and graphs shown on the DARWIN page. It is foreseen to enable their download in next releases.

##  Installation

```
pip install darwinex-data
```

### Requirements

The only required library to execute the notebook is Pandas.


## Usage

Together with your Darwinex user, you will need to request your Darwinex FTP access password at 
**[REQUEST FTP ACCESS](https://www.darwinex.com/data/darwin-data)**

Open the jupyter notebook darwinex-data.ipynb and execute it step by step.
- Indicate your Darwinex username and FTP password
- Start by connecting to the Darwinex FTP server
- Get a list of available darwins, if you don't know which to download
- For a specific list of darwins, get the available dates of quotes data to download, for a darwin may display more history on Darwinex
- Download darwin quotes, for a specific list of darwins, and a specific start and end period. Notice that the amount of data to download is huge, so you may want to filter it
- Indicate a path if you want to store the data as each darwin quotes are downloaded. It allows you to resume the dowloading process later, merging the newly downloading data with the existing one
- Possibility to resample the data before storing it, indicating a Pandas rule frequency such as 'B'. You may want to reduce the stored data size if you don't need to work with a frequency of seconds
- Close the connection to the Darwinex FTP server
- Load the downloaded pickle data to work with it

Remarks: 
- There are gaps in the darwins available quotes. These will be represented as NAN in the Pandas dataframe, letting the user to check them before filling
- Usually, each darwin has its historical data adjusted to VAR (Value At Risk) of 6.5%. It was established by Darwinex in may 2020. Before, the darwins had a VAR adjustment of 10%. These former var10 data is also available and can be optionally downloaded


## Contributing

If you find a bug or have an idea for a new feature, feel free to open an issue or submit a pull request. Please follow the contributing guidelines.


## License

This project is licensed under the MIT License. See the LICENSE file for more information.

## Contact

If you have any questions or comments about this project, you can reach me at ervelasco12@yahoo.es