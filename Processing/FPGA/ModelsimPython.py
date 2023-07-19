# Author: Kamel ABDELOUAHAB
# Company : Sma-RTy SAS
# A collection of useful rootines to invoke modelsim on images
import os
import numpy as np
from matplotlib import pyplot as plt
import shutil
import subprocess

def twosComplement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

def int2Hex(val, nbits=16):
    tmp = (val + (1 << nbits)) % (1 << nbits)
    return "{:04x}".format(tmp)

# def int2Hex(int_value):
#     return(format(int_value, 'x'))

def np2Hex(np_array, hex_filename):
    with open(hex_filename, 'w') as hex_file:
        for i, v in enumerate(np.nditer(np_array)):
            hex_gray =  int2Hex(v)
            if (i == np_array.size-1):
                hex_file.write(hex_gray)
            else: 
                hex_file.write(hex_gray+'\n')

def hex2Np(hex_filename, np_array_shape, dtype=np.int16):
    num_pixels = 1 
    for ele in np_array_shape: 
        num_pixels *= ele 
    np_array = np.zeros(num_pixels, dtype=dtype)
    with open(hex_filename, 'r') as hex_file:
        for i, line in enumerate(hex_file):
            np_array[i] = twosComplement(line, 16)

    return np_array.reshape(np_array_shape)

def simulate_no_arg(vsim_path = 'vsim', tcl_filename= 'run.tcl'):     # Execute VSIM without printing the output
    cmd = [vsim_path,  "-c", "-do", tcl_filename]
    print(cmd)
    subprocess.run(cmd, stdout=None, #subprocess.DEVNULL, 
                        stderr=None, #subprocess.DEVNULL)
                    )

def simulate(vsim_path, tcl_filename, arg_filename, generic_names, generic_values):
    arg_list = []
    for n,v in zip(generic_names, generic_values):
        arg_list.append("-g" + n + "=" + v)

    with open(arg_filename, 'w') as f:
        for item in arg_list:
            f.write("%s " % item)        

    cmd = [vsim_path, "-c", "-do", tcl_filename]
    print("Commande Run",cmd)
    subprocess.run(cmd, stdout=None, #subprocess.DEVNULL, 
                        stderr=None, #subprocess.DEVNULL)
                    )

def quit():
  subprocess.run([quit, "-force"])

def displayCompare(img_list, stats=False):
    f, axarr = plt.subplots(2,len(img_list))
    for i, img in enumerate(img_list):
        if stats:
            print("min={:.2f}, max={:.2f}, mean={:.2f}".format(np.min(img), np.max(img), np.mean(img)))
        axarr[0, i].imshow(img, cmap='gray')
        axarr[1, i].hist(img.ravel())
    plt.show()

def display(img, stats=False):
    if stats:
        print("min={:.2f}, max={:.2f}, mean={:.2f}".format(np.min(img), np.max(img), np.mean(img)))
    plt.imshow(img, cmap='gray')
    plt.show()

def quantizeArray(data, bitwidth):
    # compute scale factor from bitwidth
    scale_factor = np.power(2, (bitwidth-1)) - 1
    # round data
    scaled_data =  np.array(np.round(scale_factor * data), dtype=int)
    # saturate the values
    scaled_data[scaled_data > scale_factor] =  scale_factor
    scaled_data[scaled_data <-scale_factor] = -scale_factor
    return(scaled_data)

def clean():
    files_to_remove = ['modelsim.ini', 'transcript', 'vsim.wlf']
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
    shutil.rmtree("work")