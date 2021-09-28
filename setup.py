import os

from setuptools import setup, find_packages


install_requires = open("requirements.txt").read().splitlines()


setup(name='postproxy',
      version='0.1',
      description='PostProxy used to debug post request',
      classifiers=[
          "Programming Language :: Python",
            ],
      author='bebe',
      packages=find_packages(),
      package_data={},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=[],
      setup_requires=install_requires,
      entry_points={
          'console_scripts': ['postproxy = postproxy.postproxy:main']
      }
      )
