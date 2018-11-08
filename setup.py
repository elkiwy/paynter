import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
    name="paynter",
    version="0.1.4",
    author="Stefano Bertoli",
    author_email="elkiwydev@gmail.com",
    description="PaYnter is a Python Library that let you procedurally generate images with handy features that emulates what you can find in any image editing software like Photoshop, GIMP, Krita, and similars.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/elkiwy/paynter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)