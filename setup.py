from setuptools import setup, find_packages

setup(
    name="penis-protocol",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0",
    ],
    author="62410-group-23",
    description="PENIS Protocol for EV3 robot control",
    license="MIT",
)
