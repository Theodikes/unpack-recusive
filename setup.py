import setuptools
import os
import sys
import shutil

if sys.argv[-1] == "publish":
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        shutil.rmtree(os.path.join(here, "dist"))
    except FileNotFoundError:
        pass
    os.system('python setup.py sdist bdist_wheel')
    os.system('python -m twine upload --repository pypi dist/*')
    sys.exit()

with open("README.md", "r") as readme_file:
    pypi_lib_readme = readme_file.read()

setuptools.setup(
    name="unpack-recursive",
    version="1.0.0",
    author="Theodike",
    author_email="gvedichi@gmail.com",
    description="Recursive unpacking any type of archives",
    keywords=["recursive", "unpack archive", "unzip recursive", "unpack recursive"],
    long_description=pypi_lib_readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Theodikes/unpack-recursive",
    install_requires=["typing_extensions"],
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
