# aws-cost-and-usage
Python script which uses AWS CLI to pull down AWS cost and usage information into excel, allowing you to group the data by up to two dimentions. This uses the aws ce command [get-cost-and-usage](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/ce/get-cost-and-usage.html)

## Configuration
In order to setup the script, please populate the config.json file. This allows you to define:
- The [Credential Profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) you wish to use (use `default` if you are not using credential profiles)
- The number of months of data to pull back
- The path to write the xlsx file to
- The name of the xlsx file to write the output to
- The Schema. This are the headers written to the excel file. Columns 2 and 3 are the things you are grouping by (see the arguments). In the example config file, this is grouped by usage type and service. These can be changed to any [attributes supported by the AWS CLI](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/API_GetDimensionValues.html).
- Arguments. This defines the arguments used by the AWS CLI Command. In the example, this includes setting the granularity to monthly, and filtering the results to exclude certain types of cost. It also pulls back the unblended cost, and groups the result by the Tribe cost category and the Linked Account dimension.

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
Your results will be written to the xlsx file specified!
