from setuptools import setup

setup(
    name='pypub',
    version='2.0.0',
    packages=['pypub',],
    package_data={'pypub': ['templates/*', 'static/*', 'static/css/*', 'static/img/*', 'static/fonts/*']},
    author='Andrew Scott',
    author_email='imgurbot12@gmail.com',
    url='https://github.com/imgurbot12/pypub',
    license='MIT',
    install_requires=[
        'requests',
        'jinja2',
        'lxml',
        'pillow'
    ],
    description="Create epub's using python. Pypub is a python library to create epub files quickly without having to worry about the intricacies of the epub specification.",
)
