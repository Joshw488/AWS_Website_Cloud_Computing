# AWS_Website_Cloud_Computing
This project hosts a website in the cloud and connects multiple AWS services to allow for storage in DynamoDB and s3 buckets.

Project Description:
Purpose
This programming assignment will introduce the student to using multiple services in the cloud
working together. In particular the student will use S3 or Blob Storage, DynamoDB or Azure
Tables or CosmosDB, and website technology which allows server side code (ASP.Net, MVC,
etc…).
Problem Statement / Overview
Create and host a Website which has three sections:
1) A button call Load Data
2) A button call Clear Data
3) Two input text boxes labeled First Name and Last Name
4) A button called Query


When the “Load Data” button is hit the website will load data from an object stored at a given
URL. I will have the data both in Azure as well as Amazon S3. The CORS (Cross-Origin Resource
Sharing) header has been added to the bucket so that the object can be accessed from different
regions.

First you will copy this data (a test file) into Object storage (S3 or Blob). You will also be
required to parse and load into a <Key, Value> NoSQL store (Dynamo DB or Azure Tables). Note
that the load button can be hit multiple times. Each time the test file should be parsed and the
NoSQL DB should be updated.

When the “Clear Data” button is hit the blob is removed from the object store. The NoSQL
table is also emptied or removed.

Once the data has been loaded in the NoSQL store the Website user can type in either one or
both a First and Last name. When the Query button is hit results are shown on the Website.
For the queries the names should be exact matches. Note that you do not need to fill in both
query boxes to query.

This lab will require both the working Website as well as a design document and report. 
The lecture slides from class give students links to ASP.Net website tutorials if they need them
to get started. That said, ASP.Net is not required and the student can use any web site
infrastructure that they would like. The website should be hosted in either Amazon or Azure.
Problem Statement Details


Data Format
The blob/object can be found at the URLs noted below. The format will be a text file
with one line per item. Each line will have a last name, a first name and then a variable number
of attributes:

        lastName firstName [attribute1=value1 attibrute2=value2 attribute3=value3 …]
The attributes will not have spaces in them.
Example Data:

        Dimpsey Robert id=65764 phone=4528769876 office=trulyhouse
        Winfrey Opal id=87643 phone=8769870987 age=57
         Trevor Billy id=7638 age=81 gender=M
        Munro Alice id=9876 age=65 gender=F
        Dimpsey Pearl id=98776 phone=4528769876 office=none
        
Query

The last name / first name combination are guaranteed to be unique. A query of
“Winfrey” and “Opal” should return the attributes: id=87643 phone=8769870987 age=57. A
query of “Dimpsey” “” should return both:

        Dimpsey Robert id=65764 phone=4528769876 office=trulyhouse
        Dimpsey Pearl id=98776 phone=4528769876 office=none
