#N.B. This script does not support updating an existing excel file. The excel file specified will be over-written each time the script runs!

import boto3
import botocore
import xlsxwriter
import datetime
import json
import os
import time
from dateutil.relativedelta import relativedelta

#Open config file and populate variables
filepath = os.path.dirname(__file__) + '/config.json'
try:
	with open(filepath) as config_file:
		config_json = json.load(config_file)
		credential_profile = config_json['config_variables']['credential_profile']
		vaultname = config_json['config_variables']['vaultname']
		job_id = config_json['config_variables']['job_id']
except Exception as error:
	print('Invalid Config file, please check your syntax!')
	print('JSON Error: ', error)
	raise SystemExit(0)

initiate_job_args = {
						'vaultName': vaultname,
						'accountId': '-',
						'jobParameters': {"Type": "inventory-retrieval"}
					}
					
describe_job_args = {
						'vaultName': vaultname,
						'accountId': '-',
						'jobId': job_id
					}
					
output_job_args = {
						'vaultName': vaultname,
						'accountId': '-',
						'jobId': job_id,
					}

def initiate_inventory_job(**args):
	#Function to connect to AWS kick off the initial job
	#First checks if the Job ID is already set in the config file. If it is, this code is not run
	global job_id
	if len(job_id) == 0:
		print('Attempting to initiate the Inventory Retrieval job')
		try:
			session = boto3.Session(profile_name=credential_profile)
			client = session.client('glacier')
			response = client.initiate_job(**args)
			job_id = response['jobId']
			print('Inventory Retreival initiated, writing Job ID back to config file')
			try:
				with open(filepath, 'r') as config_file:
					config_json = json.load(config_file)
				config_json['config_variables']['job_id'] = job_id
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
		print('Job ID is already defined in the config file, assuming the Inventory Retreival job has already been initiated, so a new job will not be run.\n')
#	return job_id


def check_job_status(**args):
	#Function to check the job status once it is running
	#First checks if the Job ID is already set in the config file. If it is, this code is not run
	global job_id
	if len(job_id) == 0:
		print('Job ID is missing, which means the Inventory Job was not initiated successfully. Please correct the error and retry')
	else:
		completed = False
		while not completed:
			print('Checking the Inventory Retrieval job status')
			try:
				session = boto3.Session(profile_name=credential_profile)
				client = session.client('glacier')
				response = client.describe_job(**args)
				completed = response['Completed']
				statuscode = response['StatusCode']
				if completed:
					print('Job has completed with status code ', statuscode)
				else:
					print('Job has not yet completed, please wait this could take some time. This script will continue to run and check every minute or you can cancel it and re-run it to check the status of the job')
					print('Status Code: ',statuscode,"\n")
					time.sleep(60)
			except botocore.exceptions.ClientError as error:
				if error.response['Error']['Code'] == 'ExpiredTokenException':
					print('There has been an issue authenticating with AWS, please ensure you have a valid token named ', credential_profile, ' defined in your credentials file')
					print('Error Message: ', error.response['Error']['Message'])
				else:
					print('There has been an unknown error communicating with AWS: ', error.response)
				raise SystemExit(0)
	return completed
	

def get_job_output(**args):
	#Function to check the job status once it is running
	#First checks if the Job ID is already set in the config file. If it is, this code is not run
	global job_id
	if len(job_id) == 0:
		print('Job ID is missing, which means the Inventory Job was not initiated successfully. Please correct the error and retry')
	else:
			print('Getting Job Output \n')
			try:
				session = boto3.Session(profile_name=credential_profile)
				client = session.client('glacier')
				response = client.get_job_output(**args)
			except botocore.exceptions.ClientError as error:
				if error.response['Error']['Code'] == 'ExpiredTokenException':
					print('There has been an issue authenticating with AWS, please ensure you have a valid token named ', credential_profile, ' defined in your credentials file')
					print('Error Message: ', error.response['Error']['Message'])
				else:
					print('There has been an unknown error communicating with AWS: ', error.response)
				raise SystemExit(0)
	return json.load(response['body'])

def delete_archives(**output):
	#Function which parses through each Archive ID in the output and deletes it!
	global vaultname
	if len(job_id) == 0:
		print('Job ID is missing, which means the Inventory Job was not initiated successfully. Please correct the error and retry')
	else:
		#Loop through each item in the Archive List
		for archiveitem in output['ArchiveList']:
			archiveid = archiveitem['ArchiveId']
			try:
				print('Deleting Archive with Archive ID: ', archiveid, '\n')
				session = boto3.Session(profile_name=credential_profile)
				client = session.client('glacier')
				response = client.delete_archive(
					vaultName=vaultname,
					archiveId=archiveid
				)
				print(response, '\n')
			except botocore.exceptions.ClientError as error:
				if error.response['Error']['Code'] == 'ExpiredTokenException':
					print('There has been an issue authenticating with AWS, please ensure you have a valid token named ', credential_profile, ' defined in your credentials file')
					print('Error Message: ', error.response['Error']['Message'])
				else:
					print('There has been an unknown error communicating with AWS: ', error.response)
				raise SystemExit(0)

#Kick off the Inventory Retreival Job
initiate_inventory_job(**initiate_job_args)
#Check the status of the job until it is completed
completed = check_job_status(**describe_job_args)
if completed:
	#Get the job output and pull out the Archive IDs
	output = get_job_output(**output_job_args)
	delete_archives(**output)