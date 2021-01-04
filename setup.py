import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="mmd",
    version="0.0.1",
    author="Luca Wellmeier",
    author_email="luca_wellmeier@gmx.de",
    description="Parser for the MMD format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lucawellmeier/mmd",
    packages=setuptools.find_packages(),
    py_modules=['mmd'],
    python_requires='>=3.9.1',
)
