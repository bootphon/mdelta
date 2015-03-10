"""
"""
from scipy.linalg import cho_factor, cho_solve
from scipy.stats import entropy
import numpy as np

default_deltas = range(1, 5) + range(10, 80, 5)
b_cached = np.identity(2, np.float64)

def cos_dist(x, y):
    z = np.linalg.norm(x)*np.linalg.norm(y)
    return 1. - np.dot(x,y)/z

def symmetric_kl_div(p, q):
    eps = np.finfo(p.dtype).eps
    p += eps
    q += eps
    return entropy(p, q) + entropy(q, p)

def m_measure_delta(P, t, delta_t, negative=False, dist=symmetric_kl_div):
    T = P.shape[0]
    if negative:
        t_shifted = t-delta_t
    else:
        t_shifted = t+delta_t
    if not (0 <= t_shifted < T):
        return None
    else:
        return dist(P[t], P[t_shifted])

def m_measure_delta_avg(P, delta_t, symmetric=False, dist=symmetric_kl_div):
    T = P.shape[0]
    if delta_t >= T:
        return None
    else:
        M = 0
        n = T - delta_t
        for t in range(T - delta_t):
            M += dist(P[t], P[t + delta_t])
        if symmetric:
            n = 2*n
            for t in range(delta_t, T):
                M += dist(P[t], P[t - delta_t])
        return M / n

def mdelta_reg_with_missing_data(y, p_within_class, p_across_class):
    y_np = np.array(y, dtype=np.float64)
    y_vals = y_np[~np.isnan(y_np)]
    p_within_class = p_within_class[~np.isnan(y_np)]
    p_across_class = p_across_class[~np.isnan(y_np)]
    A = (np.array([p_within_class.T, p_across_class.T])).T
    try:
        AtAi = cho_solve(cho_factor(np.dot(A.T, A)), b_cached)
    except np.linalg.LinAlgError:
        return None, None
    x = np.dot(np.dot(AtAi, A.T), y_vals)
    return x[0], x[1]

def mdelta_avg(P, p_within_class, p_across_class, deltas=default_deltas,
            symmetric=False, dist=symmetric_kl_div):
    y = np.empty((len(deltas),))
    for i, delta_t in enumerate(deltas):
        y[i] = m_measure_delta_avg(P, delta_t, symmetric, dist)
    return mdelta_reg_with_missing_data(y, p_within_class, p_across_class)

def mdelta(P, t, p_within_class, p_across_class, deltas=default_deltas,
            negative=False, dist=symmetric_kl_div):
    y = np.empty((len(deltas),))
    for i, delta_t in enumerate(deltas):
        y[i] = m_measure_delta(P, t, delta_t, negative, dist=symmetric_kl_div)
    return mdelta_reg_with_missing_data(y, p_within_class, p_across_class)

def avg_mmeasure_on_avg(P, deltas=default_deltas, dist=symmetric_kl_div):
    M = np.empty((len(deltas)))
    for i, delta_t in enumerate(deltas):
        M[i] = m_measure_delta_avg(P, delta_t, dist)
    return np.mean(M)


