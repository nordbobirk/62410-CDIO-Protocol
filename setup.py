from setuptools import setup

setup(
    name="penis-protocol",
    version="0.1.0",
    py_modules=["protocol"],  # Single file in root
    install_requires=[
        "pydantic>=2.0",
    ],
    author="Your Name",
    description="PENIS Protocol for EV3 robot control",
    license="MIT",
)
