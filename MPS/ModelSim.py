import os
import ModelsimPython as MSP

from PIL import Image
import numpy as np
class ModelSim():
    def __init__(self,modelsim_path) -> None:
        self.modelsim_path = modelsim_path


    def __call__(self,folder_input_image):
        #list of img 
        print(folder_input_image)
        folder_hex = '/'.join(folder_input_image.split('/')[:-1]) + '/hex'
        folder_out_hex = '/'.join(folder_input_image.split('/')[:-1]) + '/out_hex'
        folder_img_sim = '/'.join(folder_input_image.split('/')[:-1]) + '/img_sim'

        if not os.path.exists(folder_hex):
            os.makedirs(folder_hex)
        if not os.path.exists(folder_out_hex):
            os.makedirs(folder_out_hex)
        if not os.path.exists(folder_img_sim):
            os.makedirs(folder_img_sim)
        
        
        for image_filename in os.listdir(folder_input_image):
            if 'png' not in image_filename:
                continue
            print(f'Processing {image_filename} ...')
            img_src_filename = os.path.join(folder_input_image,image_filename)
            img = Image.open(img_src_filename)
            img_np = np.array(img)

            img_hex_filename     = os.path.join(folder_hex, image_filename.split('.')[0] + '.hex')
            img_hex_out_filename = os.path.join(folder_out_hex, image_filename.split('.')[0] + '.hex')
            img_sim_filename     = os.path.join(folder_img_sim, image_filename.split('.')[0] + '_sim.jpg')
            print(img_src_filename)
            print(img_hex_filename)
            print(img_hex_out_filename)

            MSP.np2Hex(img_np, img_hex_filename)
            MSP.simulate(vsim_path      = os.path.join(self.modelsim_path, 'vsim'),
                 tcl_filename   = 'ModelSim/run_cli.tcl',
                 arg_filename   = 'args.txt',
                 generic_names  = ['IMG_FILENAME_IN', 'IMG_FILENAME_OUT'],
                 generic_values = [img_hex_filename, img_hex_out_filename])
        
            img_np_sim = MSP.hex2Np(img_hex_filename, img_np.shape)
            print(img_np_sim.shape)
            img_sim = Image.fromarray(img_np_sim).convert('RGB')
            img_sim.save(img_sim_filename)

if __name__ == '__main__':
    ms = ModelSim("/home/ropouillard/intelFPGA/20.1/modelsim_ase/bin/")

    ms('output/Caméra_01')

