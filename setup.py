from setuptools import setup, find_packages

setup(
    name='fmlpy',
    version='0.1.0',
#     packages=find_packages(exclude=['tests*']),
    packages=find_packages(),
    license='LICENSE',
    description='package for Financial Machine Learning',
    install_requires=['numpy','pandas'],
    url='https://github.com/crazywiden/fmlpy',
    author='Xiuyu & Yuan',
    author_email='yuangao719@gmail.com',
    keywords = ['Machine Learning', 'Financial'], 
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Financial and Insurance Industry',  
        'Programming Language :: Python :: 3'
    ]
)

