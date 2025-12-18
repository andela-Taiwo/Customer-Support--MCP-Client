from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="customer-support-chatbot",
    version="0.1",
    author="Taiwo Sokunbi",
    author_email="sokunbitaiwo82@gmail.com",
    description="Customer Support Chatbot",
    url="https://github.com/andela-Taiwo/Customer-Support--MCP-Client",
    packages=find_packages(),
    install_requires=requirements,
)
