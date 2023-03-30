from setuptools import setup, find_packages


setup(
    name="capstone",
    version="0.1.0",
    description="Guided projects for hackers",
    author="Pipal Academy",
    url="https://github.com/pipalacademy/capstone",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'capstone-server = capstone.cli:cli',
    ],        
    }
)
