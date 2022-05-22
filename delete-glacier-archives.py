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
with open(filepath) as config_file:
	config_json = json.load(config_file)
	credential_profile = config_json['config_variables']['credential_profile']
	num_months = config_json['config_variables']['num_months']
	schema = config_json['config_variables']['schema']
	path = config_json['config_variables']['path']
	wbname = config_json['config_variables']['wbname']
	args = config_json['arguments']


#Get the dates for the last num-months months
today = datetime.date.today()
end = today.replace(day=1)
start = end - relativedelta(months=num_months)
startstr = start.strftime("%Y-%m-%d")
endstr = end.strftime("%Y-%m-%d")
print('Start: ',startstr)
print('end: ',endstr)

#Add the time period to the args variable
args = args | {'TimePeriod':
						{
							'Start': startstr,
							'End': endstr
						}
					}

#Function to connect to AWS and pull the cost data as JSON
def get_awscli_json(**args):
	try:
		session = boto3.Session(profile_name=credential_profile)
		client = session.client('ce')
		response = client.get_cost_and_usage(**args)
		data = response['ResultsByTime']
		#print('Response: ', json.dumps(response, indent=4, sort_keys=True).replace('\\n','\n'))
		if "NextPageToken" in response:
			args['NextPageToken'] = response['NextPageToken']
			data += get_awscli_json(**args)
	except botocore.exceptions.ClientError as error:
		if error.response['Error']['Code'] == 'ExpiredTokenException':
			print('There has been an issue authenticating with AWS, please ensure you have a valid token named ', credential_profile, ' defined in your credentials file')
			print('Error Message: ', error.response['Error']['Message'])
		else:
			print('There has been an unknown error communicating with AWS: ', error.response)
	return data

#Function to format the JSON data as a list that can be imported into Excel
def format_data(jsonresponse):
	data = []
	for jitem in jsonresponse:
		for jitemc in jitem['Groups']:
			unblendedcost = float(jitemc['Metrics']['UnblendedCost']['Amount'])
			if unblendedcost > 0:
				data.append(
					[
						#Appends the month
						datetime.datetime.strptime(jitem['TimePeriod']['Start'], '%Y-%m-%d'),
						#Appends the First Dimension
						jitemc['Keys'][0],
						#Appends the Second Dimension
						jitemc['Keys'][1],
						#Appends the cost value
						float(jitemc['Metrics']['UnblendedCost']['Amount'])
					]
			)
	return data

def write_xlsx(data):
	headers_dict = {}
	
	# Add a worksheet.
	worksheet = workbook.add_worksheet(name='Data')
	
	# Start from the first cell. Rows and columns are zero indexed.
	lastrow = len(data)
	lastcolumn = len(schema) - 1
	
	#Creates a list of dictionaries containing the headers for the XLSX table, and applies any required formatting
	datetime_format = workbook.add_format({'num_format': 'mmm yy'})
	dollars_format = workbook.add_format({'num_format': '$#,##0.00'})
	for index in range(len(schema)):
		headers_dict[index] = {}
		headers_dict[index]['header'] = schema[index]
		if schema[index] == 'Month':
			headers_dict[index]['format'] = datetime_format
		if schema[index] == 'UnblendedCost':
			headers_dict[index]['format'] = dollars_format
	# Adds a table and writes out the headers
	worksheet.add_table(0, 0, lastrow, lastcolumn, {'data': data, 'columns': headers_dict})
#Run the API call and output to JSON
jsonresponse = get_awscli_json(**args)

data = format_data(jsonresponse)

#Create the XLSX file and write the data
print('Writing the output to ', wbname)
workbook = xlsxwriter.Workbook(wbname)
write_xlsx(data)
workbook.close()