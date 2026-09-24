"""quilt-organism — the organism layer of Quilt."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="quilt-organism",
    version="0.1.0",
    description="The organism layer of Quilt — substrate walker over corpora",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/SuperInstance/quilt-organism",
    author="SuperInstance",
    author_email="team@superinstance.dev",
    license="Apache-2.0",
    python_requires=">=3.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31",
    ],
    extras_require={
        "dev": ["requests>=2.31"],
        "orchestra": ["quilt-cli>=0.5.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
