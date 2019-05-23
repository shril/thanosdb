import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thanosdb",
    version="0.0.1",
    author="Shril Kumar",
    author_email="shril.iitdhn@gmail.com",
    description="A lightweight and fast database for Prototyping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shril/thanosdb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)