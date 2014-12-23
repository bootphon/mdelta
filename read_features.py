import numpy as np

# TODO
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

def read_features(f):
    with open(f) as fin:
        aux = np.genfromtxt(fin, delimiter=' ')
    return aux[:, 1:]

