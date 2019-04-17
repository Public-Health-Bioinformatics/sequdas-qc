from setuptools import setup, find_packages

setup (
    name='sequdas_qc',
    version='0.2',
    description='NGS DATA Upload and Data Archiving System',
    url='https://github.com/Public-Health-Bioinformatics/sequdas-qc',
    author='Jun Duan',
    author_email='duanjun1981@gmail.com',
    licence='MIT',
    keywords="NGS sequences arichive analysis",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
    	'console_scripts': [
    		'sequdas=sequdas_qc.sequdas_qc:main'
    	]
    },
    install_requires=[
        mysql-python,
        validate_email,
    ]
    project_urls={
        "Source Code": "https://github.com/Public-Health-Bioinformatics/sequdas-qc",
        "Documentation": "https://github.com/Public-Health-Bioinformatics/sequdas-qc",
    }
)
