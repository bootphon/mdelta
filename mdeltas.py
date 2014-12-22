"""
"""
from scipy.stats import entropy
import numpy as np


default_deltas = range(1, 5) + range(10, 80, 5)


def symmetric_kl_div(p, q):
    eps = np.finfo(p.dtype).eps
    p += eps
    q += eps
    return entropy(p, q) + entropy(q, p)


def m_measure_delta(P, delta_t):
    T = P.shape[0]
    if delta_t >= T:
        return 0
    else:
        M = 0
        for t in range(T - delta_t):
            M += symmetric_kl_div(P[t + delta_t], P[t])
        return M / (T - delta_t)


def mdeltas(P, p_within_class, p_across_class, deltas=default_deltas):
    y = np.empty((len(deltas),))
    for i, delta_t in enumerate(deltas):
        y[i] = m_measure_delta(P, delta_t)
    A = (np.array([p_within_class.T, p_across_class.T])).T
    x = np.dot(np.dot(np.linalg.inv(np.dot(A.T, A)), A.T), y)
    return x[1] - x[0]


def mmeasure(P, deltas=default_deltas):
    M = np.empty((len(deltas)))
    for i, delta_t in enumerate(deltas):
        M[i] = m_measure_delta(P, delta_t)

    return np.mean(M)
