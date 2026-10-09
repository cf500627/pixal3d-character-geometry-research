"""Unchanged finite-hit signed quantiles selected from Stage10D."""
import numpy as np
DEPTH_FIELDS=("median","p25","p75","IQR","p95","p95_minus_median")

def require(ok,message):
    if not ok:
        raise ValueError(message)

def signed_quantiles(values):
    """Linear empirical quantiles of finite signed samples; no abs or censoring."""
    values = np.asarray(values, dtype=np.float64)
    require(values.ndim == 1 and np.isfinite(values).all(), 'Signed quantiles require finite 1D samples')
    if not len(values):
        return {key: None for key in DEPTH_FIELDS}
    p25, median, p75, p95 = np.quantile(values, [.25, .5, .75, .95], method='linear')
    return dict(median=float(median), p25=float(p25), p75=float(p75), IQR=float(p75 - p25),
                p95=float(p95), p95_minus_median=float(p95 - median))

