from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='pypub3',
    version='1.0.2',
    license='MIT',
    author='Andrew Scott',
    author_email='imgurbot12@gmail.com',
    url='https://github.com/imgurbot12/pypub',
    description="A python3 library to generate custom epub books.",
    long_description=readme,
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    packages=find_packages(),
    install_requires=[
        'jinja2',
        'lxml',
        'pillow'
    ],
    package_data={
        'pypub': [
            'templates/*', 
            'static/*', 
            'static/css/*', 
            'static/img/*', 
            'static/fonts/*'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
