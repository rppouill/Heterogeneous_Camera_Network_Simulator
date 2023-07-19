from Processing.CPU.CPU import CPU
from Processing.FPGA.FPGA import FPGA
import os

PATH_MODELSIM = "/home/ropouillard/intelFPGA/20.1/modelsim_ase/bin/"

class Processing:
    def __init__(self,fpga_processing, cpu_processing, resolution = (480,640)):
        if fpga_processing is not None:
            self.fpga_processing = FPGA(fpga_processing["modelsim_path"],
                                        fpga_processing["input_folder"],
                                        fpga_processing["output_folder"])
        

        if cpu_processing is not None:
            qemu_files = {"dtb": cpu_processing["dtb"],
                "kernel": cpu_processing["kernel"],
                "drive": cpu_processing["drive"] }
            self.cpu_processing = CPU(cpu_processing["input_folder"],
                                      qemu_files,
                                      cpu_processing["guest2host"],
                                      cpu_processing["host2guest"],
                                      cpu_processing["QEMU_Config"],
                                      resolution = resolution)

    

    def image_processing(self, image):
        pass

    def image_preprocessing(self, image):
        self.fpga_processing(image)






if __name__ == '__main__':
    
    import argparse 
    parser = argparse.ArgumentParser(description='Test Processing')

    parser.add_argument('--modelsim_path', '-M', type=str, default=PATH_MODELSIM, help='name of the modelsim path')
    parser.add_argument('--input_folder', '-I', type=str, default=None, help='name of the input folder')

    parser.add_argument('--reader_CPU', '-R', type=str, default=None, help='name of the reader serial port')
    parser.add_argument('--writer_CPU', '-W', type=str, default=None, help='name of the writer serial port')
    parser.add_argument('--config_CPU', type=str, default="config.yaml", help='name of the config file')

    args = parser.parse_args()

    fpga_processing = None 
                      #{"modelsim_path": args.modelsim_path, \
                      # "input_folder": "./output_elbow_corridor/Camera_01/images"}
    
    cpu_processing = {"reader": args.reader_CPU, \
                      "writer": args.writer_CPU, \
                      "config": args.config_CPU }
    
    processing = Processing(fpga_processing, cpu_processing)