import pathlib
import setuptools

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="thanosdb",
    version="0.0.1",
    author="Shril Kumar",
    author_email="shril.iitdhn@gmail.com",
    description="A lightweight and fast database for Prototyping",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/shril/thanosdb",
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)