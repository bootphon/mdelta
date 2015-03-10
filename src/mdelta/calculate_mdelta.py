""" """
import mdeltas
import numpy as np
import sys
import os
from read_features import read_features
from multiprocessing import Pool
from mdeltas import symmetric_kl_div, cos_dist

def write_mdelta(f, dist=symmetric_kl_div):
    global OUT_DIR
    f_id = os.path.splitext(os.path.basename(f))[0]
    out_file = os.path.join(OUT_DIR, f_id + ".csv")
    out_hf = open(out_file, 'w')
    out_hf.write("f_id, time, direction, m_within, m_across, m_delta\n")
    features = read_features(f)
    for frame_no in range(features.shape[0]):
        m_within_pos, m_across_pos = mdeltas.mdelta(features, frame_no,
                     p_within_class, p_across_class, deltas, dist=dist)
        if m_within_pos is not None:
            m_delta_pos = m_across_pos - m_within_pos  
            out_hf.write("%s, %d, positive, %.3f, %.3f, %.3f\n" % 
                    (f_id, frame_no, m_within_pos, m_across_pos, m_delta_pos))
        else:
            out_hf.write("%s, %d, positive, NA, NA, NA\n" % (f_id, frame_no))
        m_within_neg, m_across_neg = mdeltas.mdelta(features, frame_no,
                     p_within_class, p_across_class, deltas, negative=True,
                     dist=dist)
        if m_within_neg is not None:
            m_delta_neg = m_across_neg - m_within_neg
            out_hf.write("%s, %d, negative, %.3f, %.3f, %.3f\n" % 
                    (f_id, frame_no, m_within_neg, m_across_neg, m_delta_neg))
        else:
            out_hf.write("%s, %d, negative, NA, NA, NA\n" % (f_id, frame_no))
    out_hf.close()
    
def write_mdelta_cos(f):
    write_mdelta(f, dist=cos_dist)

def write_mdelta_avg(f, symmetric, dist=symmetric_kl_div):
    global OUT_DIR
    f_id = os.path.splitext(os.path.basename(f))[0]
    out_file = os.path.join(OUT_DIR, f_id + ".csv")
    out_hf = open(out_file, 'w')
    out_hf.write("f_id, m_within, m_across, m_delta\n")
    features = read_features(f)
    m_within, m_across = mdeltas.mdelta_avg(features, p_within_class,
            p_across_class, deltas, symmetric=symmetric, dist=dist)
    if m_within is not None:
        m_delta = m_across - m_within
        out_hf.write("%s, %.3f, %.3f, %.3f\n" % (f_id, m_within,
                                                m_across, m_delta))
    else:
        out_hf.write("%s, NA, NA, NA\n" % f_id)
    out_hf.close()

def write_mdelta_avg_cos(f, symmetric):
    write_mdelta_avg(f, symmetric, cos_dist)

def write_mdelta_avg_right(f):
    write_mdelta_avg(f, symmetric=False)

def write_mdelta_avg_symm(f):
    write_mdelta_avg(f, symmetric=True)

def write_mdelta_avg_symm_cos(f):
    write_mdelta_avg(f, symmetric=True, dist=cos_dist)

if __name__ == "__main__":
    dir_name = sys.argv[1]
    ext = sys.argv[2]
    prior_prob_file = sys.argv[3]
    OUT_DIR = sys.argv[4]
    do_avg = len(sys.argv) > 5 and sys.argv[6] == "average"
    avg_symm = len(sys.argv) > 6 and sys.argv[6] == "average_symm"
    use_cos = len(sys.argv) > 7
    ncpus = 4

    prior_probs = np.genfromtxt(prior_prob_file, delimiter=',', skip_header=1)
    deltas = prior_probs[:,0].astype(int)
    p_within_class = prior_probs[:,1]
    p_across_class = prior_probs[:,2]

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    files = [os.path.join(dir_name, f) for f in os.listdir(dir_name)
                if f[-4:] == "." + ext]
    if do_avg and avg_symm:
        if use_cos:
            work_and_write_fn = write_mdelta_avg_symm_cos
        else:
            work_and_write_fn = write_mdelta_avg_symm
    elif do_avg:
        if use_cos:
            work_and_write_fn = write_mdelta_avg_cos
        else:
            work_and_write_fn = write_mdelta_avg
    else:
        if use_cos:
            work_and_write_fn = write_mdelta_cos
        else:
            work_and_write_fn = write_mdelta

    p = Pool(ncpus)
    p.map(work_and_write_fn, files)

