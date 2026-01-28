from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

from repairbox import __version__ as version

setup(
	name="repairbox",
	version=version,
	description="RepairBox",
	author="Me",
	author_email="me@example.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
