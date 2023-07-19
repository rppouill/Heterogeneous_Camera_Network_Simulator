def Elbow_Corridor(end_frame):
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
def Square(end_frame):
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

    obj['cube'][0].location = (1,4,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,0.0)

    obj['cone'][0].location = (-9,-14,0.3)
    obj['cone'][0].rotation_euler = (0.0,1.5708,0.0)

    start_frame = 1        # Set the output folder for the bpy verbosity
    update(obj,frame = start_frame)

    obj['cube'][0].location = (1,-6,0.3)
    obj['cube'][0].rotation_euler = (0.0,0.0,-1.5708)

    obj['cone'][0].location = (1,-14,0.3)
    obj['cone'][0].rotation_euler = (-1.5708,0.0,0.0)

    middle_frame = floor(end_frame/2)
    update(obj,frame = middle_frame)



    obj['cube'][0].location = (-9,-6,0.3)

    obj['cone'][0].location = (1,4,0.3)
    update(obj,frame = end_frame)

from enum import Enum
from functools import partial

class Scenario(Enum):        
    ELBOW_CORRIDOR = partial(Elbow_Corridor)
    SQUARE = partial(Square)
