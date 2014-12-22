"""
"""
import numpy as np
import mdeltas
import os
import sys

def read_phone_labels(f, fstep):
    try:
        with open(f) as label_file:
            phn_data = np.genfromtxt(label_file, delimiter=' ',
                                    names=['onset', 'offset', 'phone'],
                                    dtype="f8,f8,S5")
        onsets = phn_data['onset']
        offsets = phn_data['offset']
        phones = phn_data['phone']
        try:
            len(onsets)
        except:
            onsets = np.array([onsets])
            offsets = np.array([offsets])
            phones = np.array([phones])
        frames_per_phone = ((offsets - onsets) / fstep).astype(int)
        frames = np.repeat(phones, frames_per_phone)
        return frames
    except:
        sys.stdout.write('error with file {}\n'.format(f))
        raise

if __name__ == "__main__":
    dir_name = sys.argv[1]
    ext = sys.argv[2]
    fstep = float(sys.argv[3]) 
    out_file = sys.argv[4] 

    deltas = mdeltas.default_deltas
    n_within = np.zeros(len(deltas))
    n_total = np.zeros(len(deltas))

    files = [os.path.join(dir_name, f) for f in os.listdir(dir_name)
                if f[-4:] == "." + ext]
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
