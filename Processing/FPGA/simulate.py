import sys
import os

from PIL import Image, ImageChops
import numpy as np

import ModelsimPython as MSP

MODELSIM_PATH = "/home/ropouillard/intelFPGA/20.1/modelsim_ase/bin/"
def main(img_src_filename):
    print("Start simulation ...")
    img_hex_filename = img_src_filename.split('.')[0] + '.hex'
    img_hex_out_filename = img_src_filename.split('.')[0] + '_out.hex'


    # load image
    img = Image.open(img_src_filename)

    img_np = np.array(img)

    # convert to hex
    MSP.np2Hex(img_np, img_hex_filename)

    MSP.simulate(vsim_path      = os.path.join(MODELSIM_PATH, 'vsim'),
                 tcl_filename   = 'run_guiback.tcl',
                 arg_filename   = 'args.txt',
                 generic_names  = ['IMG_FILENAME_IN', 'IMG_FILENAME_OUT'],
                 generic_values = [img_hex_filename, img_hex_out_filename])
    
    
    img_np_sim = MSP.hex2Np(img_hex_filename, img_np.shape, dtype=np.int16)
    img_sim = Image.fromarray(img_np_sim).convert('RGB')
    img_sim.save(img_src_filename.split('.')[0] + '_sim.jpg')
    img.save('test.png')
    

    print(img_np.shape)
    print(img_np_sim.shape)
    print(np.array_equal(img_np, img_np_sim))


    def are_images_equal(img1, img2):
        equal_size = img1.height == img2.height and img1.width == img2.width

        if img1.mode == img2.mode == "RGBA":
            img1_alphas = [pixel[3] for pixel in img1.getdata()]
            img2_alphas = [pixel[3] for pixel in img2.getdata()]
            equal_alphas = img1_alphas == img2_alphas
        else:
            equal_alphas = True

        equal_content = not ImageChops.difference(
            img1.convert("RGB"), img2.convert("RGB")
        ).getbbox()

        return equal_size and equal_alphas and equal_content

    print(are_images_equal(img, img_sim))
    img.show(title='original')
    img_sim.show(title='simulated')

    print("Done !")



if __name__ == '__main__':
    import argparse 
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_src_filename','-i', type=str, help='source image filename')
    args = parser.parse_args()
    main(args.img_src_filename)