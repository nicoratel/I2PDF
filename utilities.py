import numpy as np


def convert_tth2q(tth, wavelength):
    """
    Converts two-theta angles to Q values.
    """
    tth_rad = np.radians(tth)
    q = (4 * np.pi / wavelength) * np.sin(tth_rad / 2)
    return q

def convert_qnm2qA(q_nm):
    """
    Converts Q values from nm^-1 to A^-1.
    """
    return q_nm * 10.0

def read_file(file_obj,wavelength = 0.71, unit="tth"):

    """
    file_path: str
        Path to the file to be read.
    wavelength: float
        Wavelength of the X-ray radiation.
    unit: str
        Unit of the data in the file. Can be 'tth' (two-theta) or 'q_nm' (Q values in nm^-1) or 'q_A' (Q values in A^-1).
    Reads a file and returns its content as a string.
    """
    unit = str(unit).strip().lower()
    if unit not in ["tth", "q_nm", "q_a"]:
        raise ValueError("Unit must be either 'tth' or 'q_nm' or 'q_A'.")
    elif unit == "tth":
        data = np.loadtxt(file_obj)
        tth = data[:, 0]
        intensity = data[:, 1]
        q = convert_tth2q(tth, wavelength=wavelength)
        return q, intensity
    elif unit == "q_nm":
        data = np.loadtxt(file_obj)
        q_nm = data[:, 0]
        intensity = data[:, 1]
        q_A = convert_qnm2qA(q_nm)
        return q_A, intensity
    elif unit == "q_a":
        data = np.loadtxt(file_obj)
        q_A = data[:, 0]
        intensity = data[:, 1]
        return q_A, intensity