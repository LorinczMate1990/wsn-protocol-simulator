from os.path import abspath, dirname
from setuptools import setup, find_packages

MODULE_NAME = "wsnSimulator"
DEVELOPMENT_STATUS = "1 - Beta"
PACKAGE_NAME = "wsnsimulator"

EXTRAS = {}
REQUIRES = []
CURDIR = dirname(abspath(__file__))

"""
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition("#")
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            #for_specifier = EXTRAS.setdefault(':{}'.format(specifier), [])
            #for_specifier.append(requirement)
        else:
            REQUIRES.append(line)
"""
REQUIRES = ["pygame", "seaborn"]

print(" %%%%%%%%%%%%%%%%%%%%%555555 ", REQUIRES)
"""
setup(
    name="example-pkg-YOUR-USERNAME-HERE",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description="okokok",
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
)
"""
setup(
    name = PACKAGE_NAME,
    version = 0.1,
    description="Simple WSN simulator",
    author="Mate Lorincz",
    url="https://github.com/LorinczMate1990/wsn-protocol-simulator",
    author_email="lorincz.mate@gmail.com",
    install_requires = REQUIRES,
    extras_requires = EXTRAS,
    package_dir={'': 'src'},
    packages=find_packages(where="src"),
    include_package_data=True,
    long_description="...",
    classifiers=[
        "Development Status :: %s" % DEVELOPMENT_STATUS,
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
"""
#"""