from setuptools import find_packages, setup

setup(
    name="extract-glyphs",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "Pillow>=8.4.0, <9.0",
    ],
)