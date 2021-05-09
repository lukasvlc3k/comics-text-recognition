import numpy as np
import os
import Levenshtein


def wer(r, h):
    ##print(r)
    ## print(h)
    """
    Calculation of WER with Levenshtein distance.

    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list

    Returns
    -------
    int

    Examples
    --------
    # >>> wer("who is there".split(), "is there".split())
    # >>> wer("who is there".split(), "".split())
    # >>> wer("".split(), "who is there".split())
    """
    # initialisation
    d = np.zeros((len(r) + 1) * (len(h) + 1), dtype=np.uint8)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    if d[len(r)][len(h)] / max(len(r), len(h)) > 1:
        print("Chyba ! ", d[len(r)][len(h)] / len(r))
        exit(10)

    return d[len(r)][len(h)] / max(len(r), len(h))
