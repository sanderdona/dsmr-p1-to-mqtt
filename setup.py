from setuptools import setup, find_packages

setup(
    name='dsmr-p1-to-mqtt',
    description='DSMR P1 to MQTT service',
    version='0.0.1',
    url='https://github.com/sanderdona/dsmr-p1-to-mqtt',
    author='Sander Dona',
    packages=find_packages(),
    install_requires=[
        'paho-mqtt-=1.6.1',
        'pyserial-=3.5',
        'pytz-=2021.3'
    ],
    python_requires='>=3'
)
