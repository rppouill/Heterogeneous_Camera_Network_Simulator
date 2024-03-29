# SPDX-License-Identifier: GPL-2.0-only

import yaml
import subprocess
import importlib

ROOT_OPTION = {
  'device': 'driver',
  'netdev': 'driver'
}

class Qemu:
  def load(self, file):
    cfg = yaml.load(open(file), Loader=yaml.SafeLoader)
    self.config = cfg['config']
    self.qemu = cfg['qemu']
    self.plugins = []
    self.fds = []
    for key in cfg['plugins']:
      plugin = importlib.import_module('Processing.CPU.pyqvmm.plugins.' + key).getInstance(cfg['plugins'][key])
      self.plugins.append(plugin)

  def _option(self, key, value):
    return key if value == None else '%s=%s' % (key, value)

  def _enc_option(self, key, options):
    if isinstance(options, dict):
      root_option = ROOT_OPTION[key] if key in ROOT_OPTION else '_value'
      args = [self._option(k, v) for (k, v) in options.items() if k != root_option]
      if root_option in options:
        args.insert(0, options[root_option])

      return ['-' + key, ','.join(args) ]
    elif options == None:
      return ['-' + key]
    else:
      return ['-' + key, str(options)]

  def get_arguments(self):
    args = ['-nodefaults']
    for k in self.config:
      if isinstance(self.config[k], list):
        for i in self.config[k]:
          args.extend(self._enc_option(k[:-3], i))
      else:
        args.extend(self._enc_option(k, self.config[k]))
    return args

  def register_fd(self, fd):
    self.fds.append(fd)

  def run(self):
    cmd = ['/usr/bin/qemu-system-%s'%(self.qemu['system'])]
    cmd.extend(self.get_arguments())
    print(' '.join(cmd))
    print(self.fds)
    try:
      for plugin in self.plugins:
        plugin.startup(self)

      process = subprocess.Popen(cmd, pass_fds=self.fds)
      for plugin in self.plugins:
        plugin.started(self)

      process.wait()
    finally:
      for plugin in self.plugins:
        plugin.destroy()
