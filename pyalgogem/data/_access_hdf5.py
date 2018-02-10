#
# PyAlgoGem Project
# data/add_read
#
# functions to read/write from HDF5 files
#
# Andrew Edmonds - 2018
#

import tables as tb
import tstables as ts

from pandas import DataFrame

from ._data_helpers import ensure_datetime, ensure_hdf5, get_minmax_timeseries


def append_to_datafile(symbol, data, file='data.h5'):
    """Append data (DataFrame) to HDF5 file"""
    if symbol.upper() not in ['BTC', 'ETH']:
        raise ValueError('Symbol must be BTC or ETH')
    if not isinstance(data, DataFrame):
        raise ValueError('Data must be Pandas DataFrame')
    file = ensure_hdf5(str(file))

    try:
        f = tb.open_file(file, 'a')
        if symbol.upper() == 'BTC':
            tseries = f.root.BTC._f_get_timeseries()
        else:
            tseries = f.root.ETH._f_get_timeseries()
        tseries.append(data)
        f.close()
    except:
        print("Error appending to {}".format(file))


def read_datafile(symbol, start=None, end=None, file='data.h5', all_data=True):
    """Read historical data from HDF5 file
    into in-memory DataFrame"""
    # ensure datetime parameters are valid
    # unless requesting all available data
    if not all_data:
        if not (ensure_datetime(start) | ensure_datetime(end)):
            raise ValueError('Must pass valid datetime arguments')
        # ensure start is prior to end
        if (start - end).total_seconds() >= 0:
            raise ValueError('Start time must be prior to end time')
    if symbol.upper() not in ['BTC', 'ETH']:
        raise ValueError('Symbol must be BTC or ETH')
    file = ensure_hdf5(str(file))

    try:
        with tb.open_file(file, 'r') as f:
            if symbol.upper() == 'BTC':
                ts = f.root.BTC._f_get_timeseries()
            else:
                ts = f.root.ETH._f_get_timeseries()
            if all_data:
                start, end = get_minmax_daterange(symbol, file=file)
            if start is None and end is None:
                print('No data found in {}'.format(file))
                return
            dataset = ts.read_range(start, end)
        return dataset
    except:
        print("Error reading from {}".format(file))


def get_minmax_daterange(symbol, file='data.h5'):
    """Get min and max of timeseries on HDF5 file"""
    if symbol.upper() not in ['BTC', 'ETH']:
        raise ValueError('Symbol must be BTC or ETH')
    file = ensure_hdf5(str(file))

    try:
        f = tb.open_file(file, 'r')
        if symbol.upper() == 'BTC':
            ts = f.root.BTC._f_get_timeseries()
        else:
            ts = f.root.ETH._f_get_timeseries()
        min_date, max_date = get_minmax_timeseries(ts)
        f.close()
        return min_date, max_date
    except:
        print("Error getting min-max dates from to {}".format(file))
