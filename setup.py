from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="sw-cae-helper",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="SolidWorks CAE集成助手 - 集成各类建模和仿真软件的CLI工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sw-cae-helper",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: CAD",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "cae-cli=sw_helper.cli:cli",
            "sw-helper=sw_helper.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "sw_helper": ["../data/*"],
    },
)
