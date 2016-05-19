from distutils.core import setup

setup(
    name='pypub',
    version='1.1',
    packages=['pypub',],
    package_data={'pypub': ['epub_templates/*',]},
    author = 'William Cember',
    author_email = 'wcember@gmail.com',
    url = 'https://github.com/wcember/pypub',
    license='MIT',
    install_requires=[
            'beautifulsoup4',
            'jinja2',
            'requests',
            ],
    description= "Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intricacies of the epub specification.",
)