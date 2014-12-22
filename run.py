"""
"""
import mdeltas
import numpy as np
import sys


# implement feature: phoneme classes


def load_ascii_posteriogram(f):
    with open(f) as fin:
        aux = np.genfromtxt(fin, delimiter=' ')
    return aux[:, 1:]


def mdeltas_buckeye(files, p_within_class, p_across_class,
                    load_function=load_ascii_posteriogram,
                    deltas=mdeltas.default_deltas,
                    index=None, phoneme_classes=None):
    """Calculates the M-delta measure for each 

    index: list containing the index of the phonemes on the posteriogram

    files: list of files containing the posteriograms

    load_function: callable, function that take as input a file path and returns
        the posteriogram
        by default: each file should contain a space separated posteriogram
        (n_frames, n_phonemes)

    deltas: list of time intervals on which the M-measure is calculated
    """
    for f in files:
        P = load_ascii_posteriogram(f)
        mdelta = mdeltas.mdeltas(P, p_within_class, p_across_class, deltas)
        mmeas = mdeltas.mmeasure(P, deltas)
        print f
        print mdelta
        print mmeas
        print ''


# def transform_time_centered_posteriogram(f):
#     frate = 16000
#     step = 0.01
#     with open(f) as fin:
#         aux = np.genfromtxt(fin, delimiter=' ')
#     times = aux[:, 0]
#     onsets = times - step/2
#     offsets = times + step/2
#     frames = ((offsets - onsets) * frate).astype(int)
#     posteriors = np.repeat(aux[:, 1:], frames, axis=0)
#     return posteriors


def prior_probas_buckeye(files, fstep=0.01, deltas=mdeltas.default_deltas,
                         phoneme_classes=None):
    """Calculate the prior probability within class and across class

    For each time interval delta, the probability within class (resp. across) denote
    the prior probability of a pair of frames separated by delta being instance of
    the same (resp. different) phoneme (or class of phoneme).

    files: list of files containing the labels, each file should have the following
        layout: 'onset offset phoneme', onset and offset are in seconds

    fstep: time step between the frames in seconds (or at least coherent with the
        onset offset)

    deltas: list of time intervals on which the M-measure is calculated
    """
    n_within = np.empty(len(deltas))
    n_total = np.empty(len(deltas))

    for i_file, f in enumerate(files):
        try:
            with open(f) as label_file:
                aux = np.genfromtxt(label_file, delimiter=' ',
                                    names=['onset', 'offset', 'phone'],
                                    dtype="f8,f8,S5")

            onsets = aux['onset']
            offsets = aux['offset']
            phones = aux['phone']
            try:
                len(onsets)
            except:
                onsets = np.array([onsets])
                offsets = np.array([offsets])
                phones = np.array([phones])

            #TODO: change it to a loop gathering phone at each time step (?)
            frames_per_phone = ((offsets - onsets) / fstep).astype(int)

            frames = np.repeat(phones, frames_per_phone)

            for i_delta, delta_t in enumerate(deltas):
                sames = (frames[:-delta_t] == frames[delta_t:])
                n_within[i_delta] += np.sum(sames)
                n_total[i_delta] += len(sames)

        except:
            sys.stdout.write('error with file {}\n'.format(f))
            raise

    p_within = n_within / n_total
    p_across = 1 - p_within

    return p_within, p_across
