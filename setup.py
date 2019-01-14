from setuptools import setup, find_packages

setup(
    name="mdx-wl-import",
    version="0.2",
    packages=find_packages(),
    install_requires=['Markdown>=2.6.11'],
    author="John David Pressman",
    author_email="jd@jdpressman.com",
    description=("Whistling Lobsters custom include extension. Lets you take "
                 "data from a url and include it in the rendered markdown."),
    license="MIT",
    url="https://github.com/JD-P/mdx_wl_import")
    
