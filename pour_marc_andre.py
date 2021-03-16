import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve


def baseline_subtraction(sp, lam=1e4, p=0.001, niter=10):
    """
    Applies an asymmetric least squares baseline correction to the spectra.
    (Updated April 2020: improved computing speed)

    Parameters:
        sp : array
            Input Spectrum(s), array shape = (n_spectra, n_pixels) for multiple spectra and (n_pixels,)
            for a single spectrum.
        lam : integer or float,  default = 1e4
            ALS 2nd derivative constraint that defines the smoothing degree of the baseline correction.
        p : int or float, default=0.001
            ALS positive residue weighting that defines the asymmetry of the baseline correction.
        niter : int, default=10
            Maximum number of iterations to optimize the baseline.

    Returns:
        array
            Baseline substracted spectrum(s), array shape = (n_spectra, n_pixels) for multiple spectra
            and (n_pixels,) for a single spectrum.
        array
            Baseline signal(s), array shape = (n_spectra, n_pixels) for multiple spectra
            and (n_pixels,) for a single spectrum.
    """
    # sp is forced to be a two-dimensional array
    sp = np.array(sp, ndmin=2)
    # initialization and space allocation
    baseline = np.zeros(sp.shape)  # baseline signal array
    sp_length = sp.shape[1]  # length of a spectrum
    diag = sparse.diags([1, -2, 1], [0, -1, -2], shape=(sp_length, sp_length - 2))
    diag = lam * diag.dot(diag.transpose())
    w = np.ones(sp_length)
    w_matrix = sparse.spdiags(w, 0, sp_length, sp_length)

    for n in range(0, len(sp)):
        for i in range(niter):
            w_matrix.setdiag(w)
            z = w_matrix + diag
            baseline[n] = spsolve(z, w * sp[n])
            w = p * (sp[n] > baseline[n]) + (1 - p) * (sp[n] < baseline[n])  # w is updated according to baseline
    return sp - baseline, baseline
