import os
import MPS.ModelsimPython as MSP

from PIL import Image
import logging as log
import numpy as np
class ModelSim():
    def __init__(self,modelsim_path, folder_images_input) -> None:
        self.modelsim_path = modelsim_path
        self.folder_camera = '/'.join(folder_images_input.split('/')[:-1])
        
        self.args_path = os.path.join(self.folder_camera, 'args.txt')
        self.tcl_path = os.path.join(self.folder_camera, 'run_cli.tcl')
        log.info(f'args_path: {self.args_path}')
        log.info(f'tcl_path: {self.tcl_path}')
        self.generate_tcl()

        self.folder_hex = '/'.join(folder_images_input.split('/')[:-1]) + '/hex'
        self.folder_out_hex = '/'.join(folder_images_input.split('/')[:-1]) + '/out_hex'
        self.folder_img_sim = '/'.join(folder_images_input.split('/')[:-1]) + '/img_sim'

        log.info(f'folder_hex: {self.folder_hex}')
        log.info(f'folder_out_hex: {self.folder_out_hex}')
        log.info(f'folder_img_sim: {self.folder_img_sim}')


        if not os.path.exists(self.folder_hex):
            os.makedirs(self.folder_hex)
        if not os.path.exists(self.folder_out_hex):
            os.makedirs(self.folder_out_hex)
        if not os.path.exists(self.folder_img_sim):
            os.makedirs(self.folder_img_sim)

    def generate_tcl(self):
        import re
        import os

        with open('./MPS/run_cli.tcl','r') as f:
            template_tcl = f.read()
        values = {
            'args' : self.args_path,
            'work' : self.folder_camera
        }

        after_replace = re.sub('<(.+?) placeholder>', lambda match: values.get(match.group(1)), template_tcl)
        
        with open(self.tcl_path,'w+') as f:
            f.write(after_replace)

    def file_MPS(self,input_image):
        img_src_filename     = input_image.split('/')[-1]
        img_hex_filename     = os.path.join(self.folder_hex     , img_src_filename.split('.')[0] + '.hex')
        img_hex_out_filename = os.path.join(self.folder_out_hex , img_src_filename.split('.')[0] + '.hex')
        img_sim_filename     = os.path.join(self.folder_img_sim , img_src_filename.split('.')[0] + '_sim.jpg')


        print(f'Processing {input_image} ...')

        print(f'img_src_filename: {img_src_filename}')
        print(f'img_hex_filename: {img_hex_filename}')
        print(f'img_hex_out_filename: {img_hex_out_filename}')
        print(f'img_sim_filename: {img_sim_filename}')     

        img = Image.open(input_image)
        img_np = np.array(img)

        MSP.np2Hex(img_np, img_hex_filename)
        print(img_np.shape)
        MSP.simulate(vsim_path      = os.path.join(self.modelsim_path, 'vsim'),
                tcl_filename   = self.tcl_path,
                arg_filename   = self.args_path,
                generic_names  = ['IMG_FILENAME_IN', 'IMG_FILENAME_OUT'],
                generic_values = [img_hex_filename, img_hex_out_filename])
        print(f'img_hex_out_filename: {img_hex_out_filename}')
        img_np_sim = MSP.hex2Np(img_hex_out_filename, img_np.shape)
        print(img_np_sim.shape)
        img_sim = Image.fromarray(img_np_sim).convert('RGB')
        img_sim.save(img_sim_filename)

    def folder_MPS(self,folder_input_image):
        print(folder_input_image)
        for image_filename in os.listdir(folder_input_image):
            if 'png' not in image_filename:
                continue
            self.file_MPS(os.path.join(folder_input_image,image_filename))



    def __call__(self,input):
        if os.path.isdir(input):
            self.folder_MPS(input)
        else:
            self.file_MPS(input)


if __name__ == '__main__':
    ms = ModelSim("/home/ropouillard/intelFPGA/20.1/modelsim_ase/bin/")

    ms('output/Caméra_01')

