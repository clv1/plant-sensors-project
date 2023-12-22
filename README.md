# plant-sensors-project

Plant sensors project for LMNH.
For this project, we created an ETL pipeline. This pipeline extract data from different API endpoints, transformed the data and then uploaded the information to different tables in a database.
We also produced a dashboard that allows both technical and non-technical staff to view the different trends.
The pipeline triggers every minute and also send emails when a plant is below or above it's optimum temperature


# SETUP
Run the command `bash shell_scripts/setup.sh` to setup the project locally.
This will:
- install the necessary requirements for the pipeline and dashboard.
- configure the database schema.

## Requirements
For each folder there will be a `requirements.txt` file. Once you are in the folder, you can run the following command:
- `pip3 install -r requirements.txt`

- You also need to create a `.env` file in every folder which holds:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - DB_HOST
    - DB_PORT
    - DB_USER
    - DB_NAME
    - DB_PASSWORD
    - DB_SCHEMA


## Files

- `schema.sql`: This is an SQL script that creates all the necessary tables in the database
- `login.sh`: This script allows you to log into the database

There are 4 folders apart of this repository. `Pipeline`, `Lambda`, `Dashboard`, `Terraform`

`Terraform`:
- This Folder includes necessary files to recreate AWS architecture using terraform.
- `main.tf`: This script replicates AWS architecture using terraform.04c381bd
- `variables.tf`: Necessary variables needed to run this script and the type the script accepts.

`Lambda`:
-`check_vitals.py`: This script contains code which constructs the AWS handler function to be used with AWS lambda. It checks incoming data from RDS and sends an email if a plant is unhealthy.
plants vitals and sends an email alert when a unhealthy plant is detected.
- `Dockerfile`: This is a Dockerfile and creates a docker image that runs the lambda handler


`Pipeline`:
- `extract.py` : This script connects to each plant API and extracts the data from each one.
- `transform.py` : This script transforms the extracted data into a format ready to upload.
- `load.py` : This script uploads all of the data to the databases.
`Dockerfile`: This is a Dockerfile and creates a docker image that runs the pipeline
- `test_extract.py`: This script contains tests for the functions in `extract.py`
- `test_transform.py`: This script contains tests for the functions in `transform.py`


`Dashboard`:
- `dashboard_functions.py`: This script contains all the functions for `dashboard.py`
- `dashboard.py`: This script creates the dashboard using streamlit
- `Dockerfile`: This is a Dockerfile and creates a docker image that runs the dashboard

## To make a docker image:

- To make a docker image run the command: `docker build -t "name" .`


### AWS resources
![image](https://github.com/clv1/plant-sensors-project/assets/89152728/b421ddac-daee-4534-aa3d-169f9378daff)

ECR's
- `c9-persnickety-pipeline-repo-t`
- `c9-persnickety-dashboard-repo-t`
- `c9-persnickety-lambda-repo-t`

Task Definitions
- `c9-persnickety-pipeline-td`
- `c9-persnickety-dashboard-td`

## SQL schema configuration:
![image](https://github.com/clv1/plant-sensors-project/assets/89152728/04c381bd-8713-40df-a94e-d5a16f6d338f)

### Notes:
Given that `VARCHAR(MAX)` permits text data of up to 2GB in size (?!), more specific constraints
have been placed on the length of text-based column entries.
Given that `VARCHAR(MAX)` permits text data of up to 2GB in size (?!), more specific constraints
have been placed on the length of text-based column entries.

- `VARCHAR(100)` has been applied uniformly to most entries, such as `town`, `email` and `continent`.
- `VARCHAR(300)` has been applied to the `image_url` column, since it can easily exceed 100 characters in length.
- `VARCHAR(3)` has been applied to country_abbreviation, since it is always three characters in length.

