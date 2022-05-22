#N.B. This script does not support updating an existing excel file. The excel file specified will be over-written each time the script runs!

import boto3
import botocore
import xlsxwriter
import datetime
import json
import os
from dateutil.relativedelta import relativedelta

#Open config file and populate variables
filepath = os.path.dirname(__file__) + '/config.json'
try:
	with open(filepath) as config_file:
		config_json = json.load(config_file)
		credential_profile = config_json['config_variables']['credential_profile']
		initiate_job_args = config_json['initiate_job_args']
		vault_name = config_json['config_variables']['vault_name']
		job_id = config_json['config_variables']['job_id']
except Exception as error:
	print('Invalid Config file, please check your syntax!')
	print('JSON Error: ', error)
	raise SystemExit(0)

initiate_job_args = {
						'vault-name': vault_name,
						'account-id': '-',
						'job-parameters': '{""Type"": ""inventory-retrieval""}'
					}
#Function to connect to AWS kick off the initial job
def initiate_inventory_job(**args):
	#First checks if the Job ID is already set in the config file. If it is, this code is nor run
	global job_id
	if len(job_id) == 0:
		print('Attempting to initiate the Inventory Retrieval job')
		try:
			session = boto3.Session(profile_name=credential_profile)
			client = session.client('glacier')
			response = client.initate-job(**args)
			job_id = response['jobId']
			print('Inventory Retreival initiated, writing Job ID back to config file')
			try:
				with open(filepath, 'r') as config_file:
					config_json = json.load(config_file)
				config_json['job_id'] = job_id
				with open(filepath, 'w') as config_file:
					config_json = json.dump(config_json, config_file)
				print('The Job has been initiated with the following job ID: ', job_id)
			except Exception as error:
				print('There has been an error writing the Job ID to the config file. Error: ', error)				
		except botocore.exceptions.ClientError as error:
			if error.response['Error']['Code'] == 'ExpiredTokenException':
				print('There has been an issue authenticating with AWS, please ensure you have a valid token named ', credential_profile, ' defined in your credentials file')
				print('Error Message: ', error.response['Error']['Message'])
			else:
				print('There has been an unknown error communicating with AWS: ', error.response)
	else:
		print('Job ID is already defined in the config file, assuming the Inventory Retreival job has already been initiated, so a new job will not be run.')
	return job_id


#Kick off the Inventory Retreival Job
initiate_inventory_job(**initiate_job_args)


