import os
import Processing.CPU.pyqvmm.qemu as PyQVMM
import sys
import socket
from PIL import Image
import logging as log
import numpy as np

class CPU():
    def __init__(self, input_folder, qemu_files_pattern, guest2host=None, host2guest=None, config = "config.yaml", resolution = (480,640)):
        import shutil
        self.current_folder = '/'.join(input_folder.split('/')[:-1])
        self.input_folder       = input_folder
        self.hex_folder_send    = os.path.join(self.current_folder, 'CPU_hex_send')
        self.hex_folder_recv    = os.path.join(self.current_folder, 'CPU_hex_recv')
        self.output_folder      = os.path.join(self.current_folder, 'CPU_processed')
        self.resolution = resolution

        if not os.path.exists(self.hex_folder_send):
            os.makedirs(self.hex_folder_send)
        if not os.path.exists(self.hex_folder_recv):
            os.makedirs(self.hex_folder_recv)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        log.debug(f'Input Folder: {self.input_folder}')
        log.debug(f'Hex Folder: {self.hex_folder_send}')
        log.debug(f'Output Folder: {self.output_folder}')

        self.guest2host = os.path.join(self.current_folder,guest2host)
        self.host2guest = os.path.join(self.current_folder,host2guest)

        qemu_folder_pattern = os.path.join('/'.join(qemu_files_pattern["kernel"].split('/')[:-1]))
        qemu_folder = os.path.join(self.current_folder,'qemu_files')
        shutil.copytree(qemu_folder_pattern, qemu_folder)
        
        qemu_files = {
            "dtb": os.path.join(qemu_folder, '/'.join(qemu_files_pattern["dtb"].split('/')[-1:])),
            "kernel": os.path.join(qemu_folder, '/'.join(qemu_files_pattern["kernel"].split('/')[-1:])),
            "drive": os.path.join(qemu_folder, '/'.join(qemu_files_pattern["drive"].split('/')[-1:]))
        }

        self.config = os.path.join(self.current_folder, ''.join(config.split('/')[-1:]))
        log.info(f'Config File QEMU: {self.config}')


        self.__generate_configQEMU(config, qemu_files)



        if guest2host is not None:
            self.server_guest2host= socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_guest2host.bind(self.guest2host)
            self.server_guest2host.listen()


        
        log.info("Loading QEMU")
        self.QEMU_VM = PyQVMM.Qemu()
        self.QEMU_VM.load(self.config)
        self.runQEMU_VM_NoBlock()


        if guest2host is not None:
            self.socket_guest2host, _ = self.server_guest2host.accept()
            log.info("Connected to guest2host")
        #Recv tmp
        tmp = self.recv()
        log.debug(tmp)

        log.info(self.host2guest)
        log.info(self.guest2host)

        if host2guest is not None:
            self.socket_host2guest= socket.socket(socket.AF_UNIX)
            self.socket_host2guest.connect(self.host2guest)
            log.info("Connected to host2guest")



        self.send("Hello World !\n\r")


    def __generate_configQEMU(self,config, qemu_files):
        import re
        with open(config,'r') as f:
            template_config = f.read()

        values = {
            'dtb'   : qemu_files["dtb"],
            'kernel': qemu_files["kernel"],
            'drive' : qemu_files["drive"],

            'host2guest' : self.host2guest,
            'guest2host' : self.guest2host,

            'host2guest_id' : self.host2guest.split('/')[-1],
            'guest2host_id' : self.guest2host.split('/')[-1]
        }
        after_replace = re.sub('<(.+?) placeholder>', lambda match: values.get(match.group(1)), template_config)
        with open(self.config,'w') as f:
            f.write(after_replace)

    def recv(self):
        #readable, writable, exceptional = select.select([self.reader], [], [], 0)
        #if self.reader in readable:
        #    return os.read(self.reader, 100).decode()
        #else:
        #    return 'Error !'
        data = self.socket_guest2host.recv(1024).decode()
        return data
    
    def send(self, data):
        return self.socket_host2guest.send(data.encode())

    def send_Image(self, filename, hex = False):
        import time
        start = time.time()
        img = Image.open(filename)
        img_np = np.array(img)
        filename_hex = os.path.join(self.hex_folder_send, filename.split('/')[-1].split('.')[0] + '.hex')
        self.__np2Hex(img_np, filename_hex)
        
        #Open img_hex and send line by line to the guest
        self.send('Start\n')
        with open(filename_hex, 'r') as hex_file:
            for line in hex_file:
                #send data withouth \n
                self.send(line)
        self.send('\nEnd\n')
        stop = time.time()
        log.info(f"Time to send image: {stop-start}")


    def recv_Image(self, filename):
        import time
        start = time.time()
        data = []
        while self.recv() != 'Start\n':
            pass
        log.info('Start reading image {}'.format(filename))
        data.append(self.recv().split('\n')[0])
        while data[-1] != 'End':
            data.append(self.recv().split('\n')[0])
            log.debug(data[-1])
        data.pop()

        log.info('Image {} read'.format(filename))
        log.info('Number of lines: {}'.format(len(data)))
        img_hex = os.path.join(self.hex_folder_recv, filename.split('/')[-1].split('.')[0] + '.hex')
        with open(img_hex, 'w') as f:
            for line in data:
                f.write(line+'\n')
        
        log.info(self.resolution)
        img_np = self.__hex2Np(img_hex, self.resolution)
        img = Image.fromarray(img_np).convert('L')
        img.save(os.path.join(self.output_folder, filename.split('/')[-1]))
        stop = time.time()
        log.info(f"Time to recv image: {stop-start}")        
        
    def __twosComplement(self,hexstr,bits):
        value = int(hexstr,16)
        if value & (1 << (bits-1)):
            value -= 1 << bits
        return value

    def __int2Hex(self,val, nbits=16):
        tmp = (val + (1 << nbits)) % (1 << nbits)
        return "{:04x}".format(tmp)

    def __np2Hex(self,np_array, hex_filename):
        with open(hex_filename, 'w') as hex_file:
            for i, v in enumerate(np.nditer(np_array)):
                hex_gray =  self.__int2Hex(v)
                if (i == np_array.size-1):
                    hex_file.write(hex_gray)
                else: 
                    hex_file.write(hex_gray+'\n')


    def __hex2Np(self,hex_filename, np_array_shape, dtype=np.int16):
        num_pixels = 1 
        for ele in np_array_shape: 
            num_pixels *= ele 
        np_array = np.zeros(num_pixels, dtype=dtype)
        with open(hex_filename, 'r') as hex_file:
            for i, line in enumerate(hex_file):
                np_array[i] = self.__twosComplement(line, 16)

        return np_array.reshape(np_array_shape)


    def runQEMU_VM_NoBlock(self):
        import threading
        thread = threading.Thread(target=self.QEMU_VM.run)
        thread.start()
        log.info("QEMU running")

    def runQEMU_VM(self):
        self.QEMU_VM.run()

    def close(self):
        if os.path.exists(self.guest2host):
            os.remove(self.guest2host)



if __name__ == '__main__':
    from functools import partial

    def signal_handler(cpu,sig, frame):
        log.info('You pressed Ctrl+C!')
        cpu.close()
        sys.exit(0)

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--nameReader', '-R', type=str, default=None, help='name of the reader serial port')
    parser.add_argument('--nameWriter', '-W', type=str, default=None, help='name of the writer serial port')

    parser.add_argument('--config', type=str, default="config.yaml", help='name of the config file')

    parser.add_argument('--iteration', '-n', type=int, default=10, help='number of iterations')
    
    args = parser.parse_args()

    import signal
    
    log.info(args.nameReader)
    log.info(args.nameWriter)

    cpu = CPU(guest2host = args.nameReader,
              host2guest = args.nameWriter,
              config = args.config)
    signal.signal(signal.SIGINT, partial(signal_handler,cpu))
    log.info("Running QEMU")

    log.info("Reading serial port")
    if args.nameReader is not None:
        for i in range(args.iteration):
        #while True:
            log.info(cpu.recv(),end="")
    
    log.info("Writing serial port")
    if args.nameWriter is not None:
        for i in range(args.iteration):
            log.info(cpu.send(f"Hello World {i+1} ! \n\r"))


    cpu.close()





"""
qemu-system-arm -kernel Processing/CPU/qemu_files/kernel-qemu-4.14.79-stretch \
-append "root=/dev/sda2 panic=1" \
-hda Processing/CPU/qemu_files/2017-11-29-raspbian-stretch-lite.img \
-dtb Processing/CPU/qemu_files/versatile-pb.dtb \
-cpu arm1176 -m 256 \
-M versatilepb \
-no-reboot \
-net nic -net user,hostfwd=tcp::5022-:22 \
-device virtio-serial-pci \
-chardev pipe,id=ch0,path=serial0 \
-device virtserialport,chardev=ch0,name=serial0 \
-chardev pipe,id=ch1,path=serial1 \
-device virtserialport,chardev=ch1,name=serial1
"""    