import re

def generate_json(args,rank):
    with open(args.json,'r') as f:
        template_json = f.read()


    values = {
        'name'          : f'Caméra_{rank+1:02d}',
        'input_path'    : args.input_blender,

        'output_folder' : os.path.join(args.output_folder,f'Caméra_{rank+1:02d}','images'),

        'modelsim_path': args.model_sim_path,
        'input_folder'  : os.path.join(args.output_folder,f'Caméra_{rank+1:02d}','images')
    }

    after_replace = re.sub('<(.+?) placeholder>', lambda match: values.get(match.group(1)), template_json)

    with open(f'camera_{rank+1:02d}.json','w') as f:
        f.write(after_replace)