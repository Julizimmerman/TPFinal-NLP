from setuptools import setup, find_packages

setup(
    name="gmail_node",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client>=2.0.0",
        "google-auth-httplib2>=0.1.0",
        "google-auth-oauthlib>=0.4.0",
        "langchain>=0.1.0",
        "langchain-openai>=0.0.2",
        "openai>=1.0.0",
        "python-dotenv>=0.19.0",
    ],
) 