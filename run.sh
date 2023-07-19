#!/bin/bash

#Two modes:
# 1. Run the simulation
# 2. Edit script VMs

while [[ $# -gt 0 ]]; do
  case $1 in
    -s|--simulation)
      SIMULATION=1
      SCENARIO="$2"
      CORES="$3"
      shift # past argument
      shift # past value
      ;;
    -e|--edit)
      EDIT=1
      DRIVE="$2"
      KERNEL="$3"
      DTB="$4"
      shift # past argument
      shift # past value
      ;;
    --default)
      DEFAULT=YES
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done


if [[ -v SIMULATION ]]; then
  echo "Running the simulation $SCENARIO with $CORES processes"
  rm -rf ./output_$SCENARIO/
  mpiexec -n $CORES python3 Camera.py \
          --generate \
          --json camera_XX.json \
          --input_blender ./ImageGenerator/Blender/Environment/$SCENARIO.blend \
          --output_blender ./output_$SCENARIO/ \
          --scenario $SCENARIO \
          --QEMU_Config ./Processing/CPU/config_socket.yaml \
          --dtb ./Processing/CPU/qemu_files/versatile-pb.dtb \
          --kernel ./Processing/CPU/qemu_files/kernel-qemu-4.14.79-stretch\
          --drive ./Processing/CPU/qemu_files/2017-11-29-raspbian-stretch-lite.img \
          --host2guest host2guest \
          --guest2host guest2host 

elif [[ -v EDIT ]]; then
  echo "Editing the script"
  qemu-system-arm -kernel $KERNEL \
        -append "root=/dev/sda2 panic=1" \
        -hda $DRIVE \
        -dtb $DTB \
        -cpu arm1176 -m 256 \
        -M versatilepb \
        -no-reboot \
        -net nic -net user,hostfwd=tcp::5022-:22 \
        -nographic 
else
  echo "Unknown option $1"
  exit 1
fi



#rm -rf ./output_square/
#mpiexec -n 4 python3 Camera.py \
#        --generate \
#        --json camera_XX.json \
#        --input_blender ./Blender/Environment/square.blend \
#        --output_folder ./output_square/ 
#        --scenario square 


#rm -rf ./output_elbow_corridor/
#mpiexec -n 2 python3 Camera.py \
#        --generate \
#        --json camera_XX.json \
#        --input_blender ./Blender/Environment/elbow_corridor.blend \
#        --output_folder ./output_elbow_corridor/ \
#        --scenario elbow_corridor 