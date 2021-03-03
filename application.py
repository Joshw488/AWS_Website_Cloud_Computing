from flask import Flask
from flask import render_template
from flask import request
import boto3
import botocore
from boto3 import dynamodb
from boto3.dynamodb.conditions import Key
import urllib.request
import json
        
#populate the db with the file at aws
def loadDB():
	fileName = "https://s3-us-west-2.amazonaws.com/css490/input.txt"
	tableName = "People"
	bucketName = "css436program4storage"
	saveFile = ""
	message = ""
	
    #check if table is created, not called often, just for error state
	try:
		dynamo_client = boto3.client('dynamodb')
		response = dynamo_client.list_tables()
		if not tableName in response['TableNames']:	#if its not created yet
			try:
				newTable = dynamo_client.create_table(
						TableName=tableName,
						KeySchema=[
							{
								'AttributeName': 'lastName',
								'KeyType': 'HASH'  # Partition key
							},
							{
								'AttributeName': 'firstName',
								'KeyType': 'RANGE'  # Sort key
							}
							],
							AttributeDefinitions=[
								{
									'AttributeName': 'lastName',
									'AttributeType': 'S'
								},
								{
									'AttributeName': 'firstName',
									'AttributeType': 'S'
								},

							],
							ProvisionedThroughput={
								'ReadCapacityUnits': 5,
								'WriteCapacityUnits': 5
							}
						)
				newTable.wait_until_exists()
			except Exception as e:
				message += "Unable to create table, please load again\n"
	except botocore.exceptions.ClientError as exp:
		message += "Unable to create table, please load again\n"
	except Exception as e:
		message += "Unable to create table, please load again\n"

	try:
		file = urllib.request.urlopen(fileName)
		for line in file:	#go through every line in the input file and decode the contents
			fullLine = ""
			attLine = ""
			decodedLine = line.decode("utf-8")
			saveFile += decodedLine
			counter = 1
			emptyLine = True
			for segment in decodedLine.split():	#split the line on whitespace
				emptyLine = False
				if counter == 1:	#capture the last name on the first pass
					lastName = segment
				elif counter == 2:	#capture the first name on the second pass
					firstName = segment
				else:
					innerCounter = 1
					for att in segment.split('='):	#break the attributes by the = sign and save each
						if innerCounter == 1:
							attributeName = att
						elif innerCounter == 2:
							attributeValue = att
						#print(att)
						innerCounter += 1
					attLine += ', \"' + attributeName + '\" : \"' + attributeValue + '\"'	#add the attributes to the line string in dict format
				counter += 1
			if not emptyLine:
				lastName = lastName.lower()
				firstName = firstName.lower()
				fullLine = '{\"lastName\" : \"' + lastName + '\", ' + '\"firstName\" : \"' + firstName + '\"' + attLine + '}'	#save the entire line in dict format
				try:	#convert to actual dict and upload the 
					jsonLine = json.loads(fullLine)
					dynamo_resource = boto3.resource('dynamodb')
					table = dynamo_resource.Table(tableName)
					try:		#item is found, delete and replace
						response = table.get_item(Key={'lastName' : lastName, 'firstName' : firstName})	
						table.delete_item(Key={'lastName' : lastName, 'firstName' : firstName})
						response = table.put_item(Item=jsonLine)
						message += lastName.capitalize() + " " + firstName.capitalize() + " added\n"
					except boto3.dynamodb.exceptions.DynamoDBKeyNotFoundError:	#new item, add it (depreciated with boto3, delete item just wont do anything above)
						response = table.put_item(Item=jsonLine)
						message += lastName.capitalize() + " " + firstName.capitalize() + " added\n"
					except Exception as e:
						return "Table not created yet"
				except botocore.exceptions.ClientError as exp:
					message += "Unable to connect to database\n"
				except Exception as e:
					message += "Unable to process line " + lastName.capitalize() + " " + firstName.capitalize() + "\n"
		try:	#save the input file to the bucket
			s3_resource = boto3.resource('s3')
			s3_resource.Object(bucketName, 'input.txt').put(ACL='public-read', Body=saveFile)
			message += "Saved to bucket\n"
		except botocore.exceptions.ClientError as exp:
			message += "Unable to save to bucket\n"
		except Exception as e:
			message += "Unable to save to bucket\n"
	except Exception as e:
		message += "Unable to open file, please load again\n"
	return message
    
#clear the database, delete and creeate one
def clearDB():
    message = ""
    tableName = "People"
    try:
        dynamo_resource = boto3.resource('dynamodb')
        dynamo_client = boto3.client('dynamodb')
        table = dynamo_resource.Table(tableName)
        try:
            response = table.delete()
            table.wait_until_not_exists()
            try:
                newTable = dynamo_client.create_table(
                    TableName=tableName,
                    KeySchema=[
                        {
                            'AttributeName': 'lastName',
                            'KeyType': 'HASH'  # Partition key
                        },
                        {
                            'AttributeName': 'firstName',
                            'KeyType': 'RANGE'  # Sort key
                        }
                        ],
                        AttributeDefinitions=[
                            {
                                'AttributeName': 'lastName',
                                'AttributeType': 'S'
                            },
                            {
                                'AttributeName': 'firstName',
                                'AttributeType': 'S'
                            },

                        ],
                        ProvisionedThroughput={
                            'ReadCapacityUnits': 5,
                            'WriteCapacityUnits': 5
                        }
                    )
                table.wait_until_exists()
                message += "Table cleared\n"
            except boto3.dynamodb.exceptions.ResourceInUseException:
                message += "Table is in creating or updating state, try again\n"
            except botocore.exceptions.ClientError as exp:
                message += "Unable to recreate database\n"
        except Exception as e:  #already deleted, create
            newTable = dynamo_client.create_table(
                TableName=tableName,
                KeySchema=[
                    {
                        'AttributeName': 'lastName',
                        'KeyType': 'HASH'  # Partition key
                    },
                    {
                        'AttributeName': 'firstName',
                        'KeyType': 'RANGE'  # Sort key
                    }
                    ],
                    AttributeDefinitions=[
                        {
                            'AttributeName': 'lastName',
                            'AttributeType': 'S'
                        },
                        {
                            'AttributeName': 'firstName',
                            'AttributeType': 'S'
                        },

                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
            table.wait_until_exists()
            message += "Table cleared\n"
        except boto3.dynamodb.exceptions.ResourceInUseException:
            message += "Table is in creating or updating state, try again\n"
        except Exception as e:
            message += "Unable to recreate database\n"
    except botocore.exceptions.ClientError as exp:
        message += "Unable to clear database\n"
    try:
        bucketName = "css436program4storage"
        s3 = boto3.resource('s3')
        s3.Object(bucketName, 'input.txt').delete()
        message += "input.txt deleted\n"
    except botocore.exceptions.ClientError as exp:
        message += "Unable to delete input.txt from s3\n"
    except Exception as e:
        message += "input.txt already deleted\n"
    return message
    
#query the database based on the input recieved from the user
def queryDB(firstName, lastName):
    message = ""
    firstName = firstName.strip()
    lastName = lastName.strip()
    try:    #neither is a number, continue 
        lastName = lastName.lower()
        firstName = firstName.lower()
        dynamo_client = boto3.client('dynamodb')
        dynamo_resource = boto3.resource('dynamodb')
        tableName = "People"
        table = dynamo_resource.Table(tableName)

        if firstName == "" and lastName == "":  #both are blank
            return "No names entered, please enter a first name or last name or both"
        elif firstName == "":   #only last name provided, query on last name
            response = table.query(KeyConditionExpression=Key('lastName').eq(lastName))
            if response["Count"] == 0:  #none found
                return "No one with the last name " + lastName.capitalize() + " was found"
            elif response["Count"] > 0: #one or more found, format properly
                for item in response["Items"]:
                    attributes = ""
                    for key in item:
                        if key == "firstName":
                            firname = item[key]
                        elif key == "lastName":
                            lasname = item[key]
                        else:
                            attributes += " " + key + "=" + item[key]
                    message += lasname.capitalize() + " " + firname.capitalize() + " " + attributes + "\n"
        elif lastName == "":    #only fist name provided, scan on first name
            response = table.scan(FilterExpression=Key('firstName').eq(firstName))
            if response["Count"] == 0:  #none found
                return "No one with the first name " + firstName.capitalize() + " was found"
            elif response["Count"] > 0: #one or more found, format properly
                for item in response["Items"]:
                    attributes = ""
                    for key in item:
                        if key == "firstName":
                            firname = item[key]
                        elif key == "lastName":
                            lasname = item[key]
                        else:
                            attributes += " " + key + "=" + item[key]
                    message += lasname.capitalize() + " " + firname.capitalize() + " " + attributes + "\n"
        else:   #both are provided, query with composite key
            response = table.query(KeyConditionExpression=Key('lastName').eq(lastName) & Key('firstName').eq(firstName))
            if response["Count"] == 0:  #none found
                return firstName.capitalize() + " " + lastName.capitalize() + " was not found"
            elif response["Count"] > 0: #one or more found, format properly
                for item in response["Items"]:
                    attributes = ""
                    for key in item:
                        if key == "firstName":
                            firname = item[key]
                        elif key == "lastName":
                            lasname = item[key]
                        else:
                            attributes += " " + key + "=" + item[key]
                    message += lasname.capitalize() + " " + firname.capitalize() + " " + attributes + "\n"
    except botocore.exceptions.ClientError as exp:
        return "Error quering the database"
    return message

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
@application.route("/")
def start():
    return render_template('home.html',
                            run_message = "")

@application.route("/load_form", methods=['POST'])
def load_funct():
    message = loadDB()
    return render_template('home.html',
                            run_message = message)
    
@application.route("/clear_form", methods=['POST'])
def clear_funct():
    message = clearDB()
    return render_template('home.html',
                            run_message = message)
    
@application.route("/query_form", methods=['POST'])
def query_funct():
    firstName = request.form['fname']
    lastName = request.form['lname']
    message = queryDB(firstName, lastName)
    return render_template('home.html',
                            run_message = message)


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()