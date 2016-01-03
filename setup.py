from distutils.core import setup

setup(
    name='pypub',
    version='0.4',
    packages=['pypub',],
    package_data={'pypub': ['epub_templates/*',]},
    author = 'William Cember',
    author_email = 'wcember@gmail.com',
    url = 'https://github.com/wcember/pypub',
    license='MIT',
    install_requires=[
           'jinja2',
           'lxml',
           'requests',
            ],
    description= "Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intracies of the epub specification.",
)