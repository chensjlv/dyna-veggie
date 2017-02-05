from setuptools import setup, find_packages

setup(
    name='dyna-veggie',
    packages=['dyna_veggie'],  # this must be the same as the name above
    install_requires=[
        'retrying>=1.3.3',
        'boto3>=1.4.4',
        'celery>=4.0.0'
    ],
    version='0.1',
    description='Fully compatible Celery result backend using DynamoDB',
    author='Mike Chen',
    author_email='yi.chen.it@gmail.com',
    url='https://github.com/chensjlv/dyna-veggie',  # use the URL to the github repo
    # I'll explain this in a second
    download_url='https://github.com/chensjlv/dyna-veggie/tarball/0.1',
    keywords=['Celery', 'DynamoDB', 'backend'],  # arbitrary keywords
    classifiers=[],
)
