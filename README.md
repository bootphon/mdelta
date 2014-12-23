mdelta
======

Tools for computing M-delta as described in Tetsuji et al (2014) and undocumented extensions

As in paper:
python calculate_mdelta.py data/HTKposteriors pos examples/phone_prior_defaults.csv \
                            examples/mdelta_htkpost_defaults_results average

With a separate Mdelta regression for each frame in the utterance, symmetrically on both sides of the frame:
python calculate_mdelta.py data/HTKposteriors pos examples/phone_prior_defaults.csv \
                            examples/mdelta_htkpost_defaults_results

