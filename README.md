# aws-delete-glacier archives
Python script which uses AWS CLI to delete Glacier archives in bulk.

## Configuration
In order to setup the script, please populate the config.json file. This allows you to define:
- The [Credential Profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) you wish to use (use `default` if you are not using credential profiles)

## Pre-requisites
In order for the script to work, you need to have:
- AWS CLI v2 installed
- Python 3.9 or higher
- the following python libraries:
  - boto3
  - xlsxwriter
  - json
  - os
- Appropriate credentials configured that have permission to read billing data. These can be set using the `aws configure` command.

The relevant Python libraries can be installed by running:
> pip install boto3 xlsxwriter

## Running the Script
To run the script, run:
Python get-cost-and-usage.py
