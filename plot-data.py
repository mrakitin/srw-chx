import numpy as np
import matplotlib.pyplot as plt

import srwpy.uti_plot_com as srw_io


def read_srw_file(filename, ndim=2):
    data, mode, ranges, labels, units = srw_io.file_load(filename)
    data = np.array(data)
    if ndim == 2:
        data = data.reshape((ranges[8], ranges[5]), order="C")
        photon_energy = ranges[0]
    elif ndim == 1:
        photon_energy = np.linspace(*ranges[:3])
    else:
        raise ValueError(f"The value ndim={ndim} is not supported.")

    horizontal_extent = np.array(ranges[3:5])
    vertical_extent = np.array(ranges[6:8])

    ret = {
        "data": data,
        "shape": data.shape,
        "flux": data.sum(),
        "mean": data.mean(),
        "photon_energy": photon_energy,
        "horizontal_extent": horizontal_extent,
        "vertical_extent": vertical_extent,
        "labels": labels,
        "units": units,
    }

    if ndim == 1:
        ret.update({key: np.nan for key in ["x", "y", "fwhm_x", "fwhm_y"]})

    return ret


data = read_srw_file("NSLS-II_CHX_beamline/res_int_pr_se.dat")["data"]
print(f"{data.shape = }")
plt.imshow(data)
plt.show()
