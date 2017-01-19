# https://python-packaging.readthedocs.io/en/latest/minimal.html
# For a fuller example see: https://github.com/CGATOxford/UMI-tools/blob/master/setup.py
# Or: https://github.com/CGATOxford/cgat/blob/master/setup.py

from setuptools import setup

setup(name='pipeline_genotype_QC',
      version='0.1',
      description='Genotype QC pipeline for thousands of samples and markers follows UKB protocol',
      url='https://github.com/EpiCompBio/genotype_tools',
      author='Antonio J Berlanga-Taylor',
      author_email='a.berlanga at imperial.ac.uk',
      license='GPL-3.0',
#      packages=['funniest'],
      zip_safe=False
     )
