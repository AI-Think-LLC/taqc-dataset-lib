from setuptools import setup, find_packages

setup(
    name='taqc',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "expression",
        "more-itertools",
        "pillow",
        "pytest",
    ],
)
