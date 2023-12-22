# plant-sensors-project
Plant sensors project for LMNH.


# SETUP
Run the command `bash shell_scripts/setup.sh` to setup the project locally.
This will:
- install the necessary requirements for the pipeline and dashboard.
- configure the database schema.

## Requirements
- `pip3 install -r requirements.txt`

## AWS resources
![image](https://github.com/clv1/plant-sensors-project/assets/89152728/b421ddac-daee-4534-aa3d-169f9378daff)

ECR's
- `c9-persnickety-pipeline-repo-t`
- `c9-persnickety-dashboard-repo-t`
- `c9-persnickety-lambda-repo-t`

SQL Stuff

### SQL schema configuration:
![image](https://github.com/clv1/plant-sensors-project/assets/89152728/04c381bd-8713-40df-a94e-d5a16f6d338f)

Given that `VARCHAR(MAX)` permits text data of up to 2GB in size (?!), more specific constraints 
have been placed on the length of text-based column entries. 
- `VARCHAR(100)` has been applied uniformly to most entries, such as `town`, `email` and `continent`.
- `VARCHAR(300)` has been applied to the `image_url` column, since it can easily exceed 100 characters in length.
- `VARCHAR(3)` has been applied to country_abbreviation, since it is always three characters in length.

