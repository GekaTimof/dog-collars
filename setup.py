from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
   name='dog-collars',
   version='1.0',
   description='Trying to make setup for good marks)',
   license='MIT',
   author='Timofeev Evgeniy, Lena Filipenko',
   author_email='geka.timof@mail.ru, lenaphilip@mail.ru',
   url='https://github.com/GekaTimof/dog-collars.git',
   packages=['src'],
   install_requires=requirements,
   extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
   },
   python_requires='>=3',
)