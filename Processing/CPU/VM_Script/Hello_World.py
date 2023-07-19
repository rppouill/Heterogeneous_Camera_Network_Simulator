import os
import sys
import subprocess
from PIL import Image
import numpy as np

import logging as log
log.basicConfig(level=log.DEBUG)


def twosComplement(hexstr,bits):
    value = int(hexstr,16)
    if value & (1 << (bits-1)):
        value -= 1 << bits
    return value

def hex2Np(hex_filename, np_array_shape, dtype=np.int16):
    num_pixels = 1 
    for ele in np_array_shape: 
        num_pixels *= ele 
    np_array = np.zeros(num_pixels, dtype=dtype)
    with open(hex_filename, 'r') as hex_file:
        for i, line in enumerate(hex_file):
            np_array[i] = twosComplement(line, 16)
    return np_array.reshape(np_array_shape)


    

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host2guest', type=str, default='/dev/vport0p1', help='host2guest')
    parser.add_argument('--guest2host', type=str, default='/dev/vport0p2', help='guest2host')

    args = parser.parse_args()

    file_host2guest = args.host2guest
    file_guest2host = args.guest2host

    size = (30,30)
    n_pxls = size[0]*size[1]

    host2guest = open(file_host2guest, 'r')

    hex_folder = 'hex'
    img_folder = 'img'
    if not os.path.exists(hex_folder):
        os.makedirs(hex_folder)
    if not os.path.exists(img_folder):
        os.makedirs(img_folder)

    subprocess.call(['echo "Hello World !" > {}'.format(file_guest2host)], shell=True)

    print(host2guest.readline(),end='')

    i = 0
    while i < 10:
        data = []
        while host2guest.readline() != 'Start\n':
            pass
        log.info('Start reading image {}'.format(i))
        data.append(host2guest.readline().split('\n')[0])
        while data[-1] != 'End':
            data.append(host2guest.readline().split('\n')[0])
        data.pop()
        
        log.info('Image {} read'.format(i))
        log.info('Number of lines: {}'.format(len(data)))
        img_hex_path = os.path.join(hex_folder, 'image_{}.hex'.format(i))
        img_path = os.path.join(img_folder, 'image_{}.png'.format(i))
        print(img_hex_path)
        with open(img_hex_path, 'w') as f:
            for line in data:
                f.write(line+'\n')
        
        img_np = hex2Np(img_hex_path, size)
        print(type(img_np))
        print(img_np.shape)
        img = Image.fromarray(img_np).convert('L')
        img.save(img_path)
        print('Image {} saved'.format(i))
        subprocess.call(['echo "Done!" > {}'.format(file_guest2host)], shell=True)

        subprocess.call(['echo "Start" > {}'.format(file_guest2host)], shell=True)
        with open(img_hex_path,'r') as f:
            for line in f:
                subprocess.call(['echo "{}" > {}'.format(line,file_guest2host)], shell=True)
        subprocess.call(['echo "End" > {}'.format(file_guest2host)], shell=True)
        
        log.info('Image {} sent'.format(i))

        i+=1 