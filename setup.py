from setuptools import setup
from setuptools.command.install import install

import subprocess


class InstallScripts(install):

    def run(self):
        install.run(self)
        subprocess.call("scripts/krico-setup.sh", shell=True)


setup(name='krico',
      version='1.0',
      description='',
      url='http://krico.gda.pl',
      author='',
      license='',
      packages=['krico'],
      cmdclass={'install': InstallScripts}
      )
