from setuptools import setup, find_packages

setup(
    name='erd_generator',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'sqlalchemy',
        'graphviz',
        'psycopg2'
    ],
    author='Francisco-Montanez',
    description='A library to generate Entity-Relationship Diagrams from a database schema',
)
