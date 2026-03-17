from setuptools import setup

setup(
    name="penis-protocol",
    version="0.1.0",
    packages=["penis"],
    package_dir={"penis": "."},
    py_modules=["protocol"],
    install_requires=["pydantic>=2.0"],
)
