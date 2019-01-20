from setuptools import setup, find_packages
from aqfilter.setup.setup import getSetupIni

sp=getSetupIni()

setup(
      name=sp['name'],
      version=sp['version'],
      description='AQFilter',
      long_description="'filter as you type' Widget",	#=open('README.md', encoding="utf-8").read(),
      url='http://github.com/dallaszkorben/akoteka',
      author='dallaszkorben',
      author_email='https://github.com/dallaszkorben/aqfilter',
      license='MIT',
      classifiers =[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
      ],
      packages = find_packages(),
      setup_requires=[ "pyqt5", "pyqt5-sip", "numpy", "pyttsx3", 'configparser'],
      install_requires=["pyqt5", 'pyqt5-sip', 'numpy','pyttsx3', 'configparser' ],
      package_data={
        'prala': ['setup/setup.ini'],
      },
      include_package_data = True,
      zip_safe=False)