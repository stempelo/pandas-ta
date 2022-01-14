import os
from pandas import DataFrame, DatetimeIndex, read_csv

VERBOSE = True

ALERT = f"[!]"
INFO = f"[i]"

CORRELATION = "corr"  # "sem"
CORRELATION_THRESHOLD = 0.99  # Less than 0.99 is undesirable

sample_data = read_csv(
    f"data/SPY_D.csv",
    index_col=0,
    parse_dates=True,
    infer_datetime_format=True,
    keep_date_col=True,
)
sample_data.set_index(DatetimeIndex(sample_data["date"]), inplace=True, drop=True)
sample_data.drop("date", axis=1, inplace=True)
# sample_data = sample_data[:200]       # First 200
# sample_data = sample_data[100:300]  # Decreasing Segment
# sample_data = sample_data[-200:]       # Last 200
# sample_data = sample_data[:80]

def error_analysis(df, kind, msg, icon=INFO, newline=True):
    if VERBOSE:
        s = f"{icon} {df.name}['{kind}']: {msg}"
        if newline:
            s = f"\n{s}"
        print(s)
