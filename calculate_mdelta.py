""" """
import mdeltas
import numpy as np
import sys
import os


def read_features(f):
    with open(f) as fin:
        aux = np.genfromtxt(fin, delimiter=' ')
    return aux[:, 1:]

if __name__ == "__main__":
    dir_name = sys.argv[1]
    ext = sys.argv[2]
    prior_prob_file = sys.argv[3]
    out_file = sys.argv[4]

    prior_probs = np.genfromtxt(prior_prob_file, delimiter=',', skip_header=1)
    deltas = prior_probs[:,0].astype(int)
    p_within_class = prior_probs[:,1]
    p_across_class = prior_probs[:,2]

    out_hf = open(out_file, 'w')
    out_hf.write("f_id, m_delta, m_measure\n")
    files = [os.path.join(dir_name, f) for f in os.listdir(dir_name)
            if f[-4:] == "." + ext]
    for f in files:
        f_id = os.path.splitext(os.path.basename(f))[0]
        features = read_features(f)
        m_delta = mdeltas.mdeltas(features, p_within_class, p_across_class,
                                    deltas, b_)
        m_measure = mdeltas.mmeasure(features, deltas)
        out_hf.write("%s, %.3f, %.3f\n" % (f_id, m_delta, m_measure))
    out_hf.close()

