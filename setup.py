import soylemma
import setuptools
from setuptools import setup, find_packages


with open('README.md', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="soylemma",
    version=soylemma.__version__,
    author=soylemma.__author__,
    author_email='soy.lovit@gmail.com',
    description="Trained Korean Lemmatizer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/lovit/korean_lemmatizer',
    packages=setuptools.find_packages(),
    package_data={
        'soylemma':[
            'dictionary/default/*',
            'dictionary/demo/*'
        ]
    },
    keywords = [
        'korean-nlp',
        'nlp',
        'lemmatizer',
    ],
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
