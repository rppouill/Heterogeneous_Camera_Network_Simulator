import sys
sys.path.append( './ModelSim' )

from ModelSim import ModelSim
from Blender.blender import Blender_Render

import numpy as np
import os

import logging as log
log.basicConfig(level=log.DEBUG, format='%(filename)s:%(lineno)s - [%(asctime)s %(levelname)s %(funcName)20s()  %(threadName)s] %(message)s')

class Simulateur():
    def __init__(self, blender_environment, modelsim_environment) -> None:

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
        
        self.modelSim = ModelSim(modelsim_environment["modelsim_path"])
        

    

def scenario(end_frame):
    import bpy
    from numpy import floor

    def update(obj,frame):
        for value in obj.values():
            for item in value:
                item.keyframe_insert("rotation_euler", frame = frame)
                item.keyframe_insert("location", frame = frame)

    cube = bpy.data.objects['Cube']
    cone = bpy.data.objects['Cône']

    obj = {'cube': [cube], 'cone': [cone]}

    obj['cube'][0].location = (0,0,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,0.0)

    obj['cone'][0].location = (9,8,0.3)
    obj['cone'][0].rotation_euler = (1.5708,0.0,0.0)

    start_frame = 1
    update(obj,frame = start_frame)

    obj['cube'][0].location = (9,0,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,1.5708)

    obj['cone'][0].location = (9,0,1.3)
    obj['cone'][0].rotation_euler = (1.5708,0.0,-1.5708)
    
    middle_frame = floor(end_frame/2)
    update(obj,frame = middle_frame)


    obj['cube'][0].location = (9,7,0.3)
    obj['cone'][0].location = (0.3,0,0.3)
    cube.location = (9,8,0.3)
    update(obj,frame = end_frame)



def json_load(filename):
    import json
    f = open(filename,'r')
    data = json.load(f)

    for config in data['Blender']:
        blender_environment = {}
        for key,value in config.items():
            blender_environment[key] = value
        blender_environment["scenario"] = scenario


    for config in data['ModelSim']:
        modelsim_environment = {}
        for key,value in config.items():
            modelsim_environment[key] = value

    return blender_environment,modelsim_environment


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Simulateur')
    parser.add_argument('--generate', '-g', action='store_true', help='generate json file (default: False)')
    parser.add_argument('--json', '-j', type=str, default='camera_XX.json', help='json file')

    #group = parser.add_mutually_exclusive_group()
    #group.add_argument('--mpi_core', '-m', type=int, default=None, help='number of mpi core (default: None)')
    #group.add_argument('--n_core', '-n', type=int, default=1, help='number of core (default: 1) if mpi_core is None')

    parser.add_argument('--input_blender', '-b', type=str, default=None, help='input blender file (default: None')
    parser.add_argument('--output_folder', '-i', type=str, default=None, help='input folder (default: None)')    

    parser.add_argument('--model_sim_path', '-p', type=str, default='/home/ropouillard/intelFPGA/20.1/modelsim_ase/bin/', help='modelsim path (default: None)')

    args = parser.parse_args()


    rank = 0

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    if args.generate:
        from utils import generate_json
        generate_json(args.json,rank)

        
    path = f'camera_{rank+1:02d}.json'
    blender_environment, modelsim_environment = json_load(path)

    if not os.path.exists(blender_environment["output_folder"]):
        os.makedirs(blender_environment["output_folder"])

    distance = [0]*blender_environment["frame"]

    Sim = Simulateur(blender_environment, modelsim_environment)
    Sim.image_generator.scenario(blender_environment["frame"])

    log.getLogger("PIL.PngImagePlugin").setLevel(log.CRITICAL + 1)

    bar_name = ['image_' + str(i) for i in range(0,blender_environment["frame"])]
    for frame in range(1,blender_environment["frame"]+1):
        Sim.image_generator.render_image(frame,
                                         distance, 
                                         filepath = blender_environment["output_folder"])
        
        Sim.modelSim(modelsim_environment["input_folder"])



    import matplotlib.pyplot as plt
    import pylab
    log.getLogger('matplotlib').setLevel(log.WARNING)

    plt.bar(range(0,blender_environment["frame"]),np.multiply(distance,1), width = 0.05)
    plt.scatter(range(0,blender_environment["frame"]),np.multiply(distance,1), s = 40)
    pylab.xticks(range(0,blender_environment["frame"]),bar_name, rotation = 45)

    for i, v in enumerate(distance):
        plt.text(i - 0.15, v + 0.2, str(round(v, 2)), fontweight='bold')

    plt.savefig(f'{blender_environment["output_folder"]}/distance.png')
    

    
