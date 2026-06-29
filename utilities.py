import numpy as np


def convert_tth2q(tth, wavelength):
    """
    Converts two-theta angles to Q values.
    """
    tth_rad = np.radians(tth)
    q = (4 * np.pi / wavelength) * np.sin(tth_rad / 2)
    return q

def read_file(file_obj,wavelength = 0.71, unit="tth"):

    """
    file_path: str
        Path to the file to be read.
    wavelength: float
        Wavelength of the X-ray radiation.
    unit: str
        Unit of the data in the file. Can be 'tth' (two-theta) or 'q' (Q values).
    Reads a file and returns its content as a string.
    """
    unit = unit.lower()
    if unit not in ["tth", "q"]:
        raise ValueError("Unit must be either 'tth' or 'q'.")  
    elif unit == "tth":
        data = np.loadtxt(file_obj)
        tth = data[:, 0]
        intensity = data[:, 1]
        q = convert_tth2q(tth, wavelength=wavelength)
        return q, intensity
    elif unit == "q":
        data = np.loadtxt(file_obj)
        q = data[:, 0]
        intensity = data[:, 1]
        return q, intensity