"""Unchanged Stage9C-R metric functions; thresholds set by the caller configuration."""
import math
import numpy as np
H=TN=TD=None
THRESHOLDS=None

def configure(config):
    global H,TN,TD,THRESHOLDS
    H=float(config["h_world"])
    TN=float(config["T_normal_degrees"])
    TD=float(config["T_depth_world"])
    THRESHOLDS=tuple(config["depth_thresholds_h"])
    if H != 1/1024:
        raise ValueError("Inherited metric unit label and >2h protocol require h=1/1024")

def quantiles(values):
    values=np.sort(np.asarray(values,np.float64));assert not np.isnan(values).any() and (values>=0).all()
    out={}
    for name,q in [('median',.5),('p90',.9),('p95',.95),('p99',.99)]:
        if not len(values):out[name]=None;continue
        at=(len(values)-1)*q;lo=int(math.floor(at));hi=int(math.ceil(at));frac=at-lo
        value=values[lo] if lo==hi or frac==0 else np.inf if np.isinf(values[hi]) else values[lo]+(values[hi]-values[lo])*frac
        out[name]='INF' if np.isinf(value) else float(value)
    return out


def metric(mask,n,u,d,miss):
    count=int(mask.sum());valid=np.isfinite(n);finite_depth=np.isfinite(d)
    def rate(total,den=count):return total/den if den else None
    def fraction(condition):
        total=int((mask&condition).sum());return dict(count=total,rate=rate(total))
    old_n=(n>TN)|~valid;new_n=(u>TN)|~np.isfinite(u)
    out=dict(visible_pixels=count,normal=dict(oriented_failure=fraction(old_n),unoriented_failure=fraction(new_n),
      orientation_only_failure=fraction(old_n&~new_n),target_miss=fraction(miss),undefined_normal_nonmiss=fraction(~valid&~miss),
      valid_normal_pixels=int((mask&valid).sum()),
      oriented_failure_rate_given_valid_normal=rate(int((mask&valid&(n>TN)).sum()),int((mask&valid).sum())),
      unoriented_failure_rate_given_valid_normal=rate(int((mask&valid&(u>TN)).sum()),int((mask&valid).sum()))),
      depth=dict(unit='h=1/1024 world',all_visible_quantiles_h=quantiles(d[mask]),finite_hit_pixels=int((mask&finite_depth&~miss).sum()),
        finite_hit_only_quantiles_h=quantiles(d[mask&finite_depth&~miss]),target_misses=int((mask&miss).sum()),
        exceed={str(x):fraction(d>x) for x in THRESHOLDS},original_T_depth_exceed=fraction(d>TD/H)),
      hole=dict(combined=fraction(miss|(d>2)),target_miss=fraction(miss),far_hit_gt2h=fraction(~miss&(d>2))),
      comparison_only_original_depth=dict(oriented_combined=fraction(old_n|(d>TD/H)),unoriented_combined=fraction(new_n|(d>TD/H))))
    assert out['hole']['combined']['count']==out['hole']['target_miss']['count']+out['hole']['far_hit_gt2h']['count']
    return out


