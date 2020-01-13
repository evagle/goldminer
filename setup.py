# coding: utf-8
import os

from setuptools import find_packages, setup

scripts = []

for root, dirs, files in os.walk("scripts", topdown=False):
    for name in files:
        scripts.append(os.path.join(root, name))

packages = find_packages(exclude=['tests*', 'scripts*', 'investigation*'])

setup(name='GoldMinder',
      version='1.0',
      description='Gold minder project of quantitative investment.',
      author='Brian',
      author_email='huangbingliang@yeah.net',
      packages=packages,
      scripts=scripts,
      license='priviate',
      install_requires=[
          'numpy',
          'pandas',
          'pymysql',
          'xlrd',
          'tushare',
          'bs4',
          'sqlalchemy',
          'TA-Lib',
          'lxml',
          'requests',
          'fake-useragent',
          'gm'
      ],
      classifiers=[
          'Development Status :: 1 - Development/Unstable',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'Topic :: Python :: Quantitative',
          'Topic :: Financial :: Investment',
      ],
      )
