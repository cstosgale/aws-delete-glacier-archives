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

## What the script does
The script will perform the following operations in order to delete your archives:
- Initiate an inventory job. This will inventory your vault and give you the IDs of the archives.
- This job will take some time to run, so the script will check the job status ever minute until it is complete (this can take many hours!).
- Once it is complete, it will get the job output, which will include a list of all of the Archive IDs in the vault
- It will then iterate through each of the job archives to delete it
- Once all the archives are deleted, an inventory job will be re-run which will update the AWS console with the fact that there are no archives in the vault
- The script won't currently check that this has completed, but simply go back to your console in 24 hours and you should find all of the archives have disappeared and you can go ahead and delete the vault!

Please note you don't have to leave the script running while you wait for the first inventory job to run. You can leave it and run it again and it will check the status of the original job. The Job ID is written to the config file automatically so if the script is re-run it will use that Job ID and not create a new job.
Please note, don't leave it for longer than 24 hours to check it as once the job is complete, the data will only persist for 24 hours before being deleted! A this point you will have to start again!

## Running the Script
To run the script, run:
Python get-cost-and-usage.py
