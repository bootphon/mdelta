"""
"""

import numpy as np
import mdeltas
import os
import sys
from read_features import read_phone_labels

if __name__ == "__main__":
    dir_name = sys.argv[1]
    ext = sys.argv[2]
    fstep = float(sys.argv[3]) 
    out_file = sys.argv[4] 

    deltas = mdeltas.default_deltas
    n_within = np.zeros(len(deltas))
    n_total = np.zeros(len(deltas))

    if ext[0] != ".":
        ext = "." + ext

    files = []
    for subdir, _, curr_files in os.walk(dir_name):
        files += [os.path.join(subdir, f) for f in curr_files\
                    if os.path.splitext(f)[1] == ext] 
    for f in files:
        phone_labels = read_phone_labels(f, fstep)
        for i_delta, delta_t in enumerate(deltas):
            sames = (phone_labels[:-delta_t] == phone_labels[delta_t:])
            n_within[i_delta] += np.sum(sames)
            n_total[i_delta] += len(sames)
    p_within = n_within / n_total
    p_across = 1 - p_within

    f_out = open(out_file, 'w')
    f_out.write("delta, prior_within, prior_across\n")
    for i in range(len(deltas)):
        f_out.write("%d, %.3f, %.3f\n" % (deltas[i], p_within[i], p_across[i]))
    f_out.close()
