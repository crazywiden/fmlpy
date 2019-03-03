from setuptools import setup, find_packages

setup(
    name='pyfml',
    version='0.1dev',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='package for Financial Machine Learning',
    long_description=open('README.txt').read(),
    install_requires=['numpy','pandas'],
    url='https://github.com/crazywiden/pyfml',
    author='My King&Yuan',
    author_email='yuangao719@gmail.com'
)