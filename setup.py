from setuptools import setup

setup(
    name='pypub',
    version='1.5',
    packages=['pypub',],
    package_data={'pypub': ['epub_templates/*',]},
    author = 'William Cember',
    author_email = 'wcember@gmail.com',
    url = 'https://github.com/wcember/pypub',
    license='MIT',
    install_requires=[
            'MarkupSafe==1.1.1',
            'beautifulsoup4==4.9.3',
            'jinja2==2.11.3',
            'requests==2.22.0',
            ],
    description= "Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intricacies of the epub specification.",
)