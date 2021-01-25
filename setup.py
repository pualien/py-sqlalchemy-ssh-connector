import os

from setuptools import setup, find_packages


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def _pip_requirement(req):
    if req.startswith('-r '):
        _, path = req.split()
        return reqs(*path.split('/'))
    return [req]


def _reqs(*f):
    return [
        _pip_requirement(r) for r in (
            strip_comments(l) for l in open(
            os.path.join(os.getcwd(), 'requirements', *f)).readlines()
        ) if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


setup(name='sqlalchemy-connector',
      version='0.1.23',
      url='https://github.com/pualien/py-sqlalchemy-ssh-connector',
      license='MIT',
      author='Matteo Senardi',
      author_email='pualien@gmail.com',
      description='Python library to connect to SQLAlchemy with SSH Tunnel',
      packages=find_packages(exclude=['tests']),
      install_requires=reqs('default.txt'),
      long_description=open('README.md').read(),
      zip_safe=False,
      long_description_content_type='text/markdown',
      python_requires='~=3.6',
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Topic :: Software Development :: Libraries :: Application Frameworks",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ])
