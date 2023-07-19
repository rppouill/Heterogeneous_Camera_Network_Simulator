import sys
#sys.path.append( './Processing/FPGA/' )

#from Processing.FPGA.FPGA import FPGA
from Processing.Processing import Processing
from ImageGenerator.Blender.blender import Blender_Render

import numpy as np
import os

import logging as log
log.basicConfig(level=log.INFO, format='%(filename)s:%(lineno)s - [%(asctime)s %(levelname)s %(funcName)20s()  %(threadName)s] %(message)s')

class Camera():
    def __init__(self, blender_environment, modelsim_environment, cpu_environment) -> None:

        params = {
            "frame" : blender_environment["frame"],
            "fps" : blender_environment["fps"],
            "resolution_x" : blender_environment["resolution"][0],
            "resolution_y" : blender_environment["resolution"][1],
            "color_mode" : blender_environment["color_mode"]
        }

        self.image_generator = Blender_Render(blender_environment["input_path"],
                                        blender_environment["output_folder"],
                                        params,
                                        blender_environment["scenario"],
                                        camera_Name= blender_environment["camera"])
        log.debug(f'{modelsim_environment}')
        
        self.proc = Processing(modelsim_environment, cpu_environment, resolution = blender_environment["resolution"])
        #self.fpga_Processing = FPGA(modelsim_environment["modelsim_path"],
        #                     modelsim_environment["input_folder"],
        #                     modelsim_environment["output_folder"])
        
    def __call__(self):
        self.image_generator()
         #self.fpga_Processing(self.image_generator.output_folder)



def redirect_print(output_folder):
    # Set the output folder for the verbosity
    logfile = os.path.join(output_folder,"logfile.log")
    open(logfile, 'a').close()
    old = os.dup(sys.stdout.fileno())
    sys.stdout.flush()
    os.close(sys.stdout.fileno())
    fd = os.open(logfile, os.O_WRONLY)

    return logfile,old,fd

if __name__ == '__main__':
    
    from utils import parser, json_load
    args = parser()
    
    rank = 0

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    if args.generate:
        from utils import generate_json
        generate_json(args,rank)

    from Scenario import Scenario
    path = f'camera_{rank+1:02d}.json'


    camera_environment, blender_environment, modelsim_environment, cpu_environment = json_load(path, Scenario[args.scenario.upper()].value)

    if not os.path.exists(blender_environment["output_folder"]):
        os.makedirs(blender_environment["output_folder"])

    #logfile,old,fd = redirect_print(camera_environment["camera_folder"])
    #blender_environment["frame"] = 10
    distance = [0]*blender_environment["frame"]

    print(camera_environment)
    print(blender_environment)
    print(modelsim_environment)
    print(cpu_environment)
    
    Sim = Camera(blender_environment, modelsim_environment, cpu_environment)
    Sim.image_generator.scenario(blender_environment["frame"])

    log.getLogger("PIL.PngImagePlugin").setLevel(log.CRITICAL + 1)

    bar_name = ['image_' + str(i) for i in range(0,blender_environment["frame"])]
    for frame in range(1,blender_environment["frame"]+1):
        log.info(f'Camera {rank+1}: Processing frame {frame}')
        filename_Blender = Sim.image_generator.render_image(frame,
                                         distance, 
                                         filepath = blender_environment["output_folder"])
        if filename_Blender is None:
            continue
        print("Filename",filename_Blender)
        filename_FPGA = Sim.proc.fpga_processing(filename_Blender)
        Sim.proc.cpu_processing.send_Image(filename_FPGA)
        log.info(Sim.proc.cpu_processing.recv())
        Sim.proc.cpu_processing.recv_Image(f'{frame}.png')



    import matplotlib.pyplot as plt
    import pylab
    log.getLogger('matplotlib').setLevel(log.WARNING)

    plt.bar(range(0,blender_environment["frame"]),distance, width = 0.05)
    plt.scatter(range(0,blender_environment["frame"]),distance, s = 40)
    #pylab.xticks(range(0,blender_environment["frame"]),bar_name, rotation = 45)

    for i, v in enumerate(distance):
        plt.text(i - 0.15, v + 0.2, str(round(v, 2)), fontweight='bold')

    folder_fig = '/'.join(blender_environment["output_folder"].split('/')[:-2])
    file_fig = f'{folder_fig}/distance_{rank+1:02d}.png'
    plt.grid()
    plt.savefig(file_fig)
    

    #os.close(fd)
    #os.dup(old)
    #os.close(old)

    
