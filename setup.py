from setuptools import setup, find_packages

setup(
    name = 'pychords',
    version = '1.0',
    description = 'Tool for processing song lyrics in ChrodPro format',
    url = 'https://github.com/mnezerka/pychords',
    author='Michal Nezerka',
    author_email='michal.nezerka@gmail.com',
    licence = 'MIT',
    keywords = 'chordpro',
    packages = find_packages(),
    install_requires = ['reportlab'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    entry_points = {
        'console_scripts': [ 'pychords=pychords.main:main']
    },
    include_package_data = True,
)
