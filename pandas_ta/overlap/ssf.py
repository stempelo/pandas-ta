# -*- coding: utf-8 -*-
from pandas_ta import np, pd
from pandas_ta.utils import get_offset, verify_series

try:
    from numba import njit
except ImportError:
    njit = lambda _: _


@njit
def np_ssf(x: np.ndarray, n: int, pi: float, sqrt2: float):
    """Ehler's Super Smoother Filter
    http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
    """
    m, ratio, result = x.size, sqrt2 / n, np.copy(x)
    a = np.exp(-pi * ratio)
    b = 2 * a * np.cos(180 * ratio)
    c = a * a - b + 1

    for i in range(2, m):
        result[i] = 0.5 * c * (x[i] + x[i - 1]) + b * result[i - 1] \
            - a * a * result[i - 2]

    return result


@njit
def np_ssf_everget(x: np.ndarray, n: int, pi: float, sqrt2: float):
    """John F. Ehler's Super Smoother Filter by Everget (2 poles), Tradingview
    https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
    """
    m, arg, result = x.size, pi * sqrt2 / n, np.copy(x)
    a = np.exp(-arg)
    b = 2 * a * np.cos(arg)

    for i in range(2, m):
        result[i] = 0.5 * (a * a - b + 1) * (x[i] + x[i - 1]) \
            + b * result[i - 1] - a * a * result[i - 2]

    return result


def ssf(close, length=None, everget=None, pi=None, sqrt2=None, offset=None, **kwargs):
    """Ehler's Super Smoother Filter (SSF) © 2013

    John F. Ehlers's solution to reduce lag and remove aliasing noise with his
    research in aerospace analog filter design. This implementation had two
    poles. Since SSF is a (Resursive) Digital Filter, the number of poles
    determine how many prior recursive SSF bars to include in the filter design.

    For Everget's calculation on TradingView, set arguments:
        pi = np.pi, sqrt2 = np.sqrt(2)

    Sources:
        http://traders.com/documentation/feedbk_docs/2014/01/traderstips.html
        https://www.tradingview.com/script/VdJy0yBJ-Ehlers-Super-Smoother-Filter/
        https://www.mql5.com/en/code/588

    Args:
        close (pd.Series): Series of 'close's
        length (int): It's period. Default: 20
        everget (bool): Everget's implementation of ssf that uses pi instead of
            180 for the b factor of ssf. Default: False
        pi (float): The value of PI to use. The default is Ehler's
            truncated value 3.14159. Adjust the value for more precision.
            Default: 3.14159
        sqrt2 (float): The value of sqrt(2) to use. The default is Ehler's
            truncated value 1.414. Adjust the value for more precision.
            Default: 1.414
        offset (int): How many periods to offset the result. Default: 0

    Kwargs:
        fillna (value, optional): pd.DataFrame.fillna(value)
        fill_method (value, optional): Type of fill method

    Returns:
        pd.Series: New feature generated.
    """
    # Validate Arguments
    length = int(length) if isinstance(length, int) and length > 0 else 20
    everget = bool(everget) if isinstance(everget, bool) else False
    pi = float(pi) if isinstance(pi, float) and pi > 0 else 3.14159
    sqrt2 = float(sqrt2) if isinstance(sqrt2, float) and sqrt2 > 0 else 1.414
    close = verify_series(close, length)
    offset = get_offset(offset)

    if close is None: return

    # Calculate Result
    np_close = close.values
    if everget:
        ssf = np_ssf_everget(np_close, length, pi, sqrt2)
    else:
        ssf = np_ssf(np_close, length, pi, sqrt2)
    ssf = pd.Series(ssf, index=close.index)

    # Offset
    if offset != 0:
        ssf = ssf.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ssf.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ssf.fillna(method=kwargs["fill_method"], inplace=True)

    # Name & Category
    ssf.name = f"SSF{'e' if everget else ''}_{length}"
    ssf.category = "overlap"

    return ssf
