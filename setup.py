from setuptools import setup

setup(name='azure_vm_launch',
      version='0.1.0',
      description='To launch azure vm',
      long_description=open('README.md').read(),
      url='https://github.com/samarthg/azure_vm_launch',
      download_url = 'https://github.com/samarthg/azure_vm_launch/archive/v0.1.0.tar.gz',
      author='Samarth Gahire',
      author_email='samarth.gahire@gmail.com',
      license='MIT',
      packages=['launch_vm'],
      install_requires=[
          'azure',
          'bumpversion',
          'fabric3',
      ],
      zip_safe=False,
      entry_points={
          'console_scripts': [
          ]
      },
      keywords = ['azure', 'vm', 'launch'],
      )
