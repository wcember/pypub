from setuptools import setup

setup(
    name='pypub',
    version='1.5',
    packages=['pypub',],
    package_data={'pypub': ['templates/*', 'static/*', 'static/css/*', 'static/img/*', 'static/fonts/*']},
    author='William Cember',
    author_email='wcember@gmail.com',
    url='https://github.com/wcember/pypub',
    license='MIT',
    install_requires=[
        'requests',
        'jinja2',
        'lxml',
        'pillow'
    ],
    description="Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intricacies of the epub specification.",
)
