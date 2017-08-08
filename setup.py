from setuptools import setup, find_packages

setup(
    name='dyna-veggie',
    packages=['dyna_veggie'],  # this must be the same as the name above
    install_requires=[
        'retrying>=1.3.3',
        'boto3>=1.4.4',
        'celery>=4.0.0'
    ],
    version='0.3.6',
    description='Fully compatible DynamoDB result backend for Celery',
    long_description=open('README').read(),
    author='Mike Chen',
    author_email='yi.chen.it@gmail.com',
    url='https://github.com/chensjlv/dyna-veggie',  # use the URL to the github repo
    # I'll explain this in a second
    download_url='https://github.com/chensjlv/dyna-veggie/tarball/0.3.6',
    keywords=['Celery', 'DynamoDB', 'backend'],  # arbitrary keywords
    classifiers=[],
)
