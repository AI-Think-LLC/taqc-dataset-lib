from setuptools import setup, find_packages

setup(
    name='taqc-dataset-lib',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        "expression>=5.0.2",
        "more-itertools>=10.2.0",
        "pillow>=10.3.0",
        "pytest>=8.1.1",
    ],
)
