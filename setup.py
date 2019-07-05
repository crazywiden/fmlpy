from setuptools import setup, find_packages

setup(
    name='fmlpy',
    version='0.10dev',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='package for Financial Machine Learning',
    long_description=open('README.md').read(),
    install_requires=['numpy','pandas'],
    url='https://github.com/crazywiden/pyfml',
    author='Xiuyu&Yuan',
    author_email='yuangao719@gmail.com',
    keywords = ['Machine Learning', 'Financial'], 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)

