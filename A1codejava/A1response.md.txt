Assignment 1 - REST API Project - Response to Criteria
================================================

Overview
------------------------------------------------

- **Name:** Lahan Kiliparamban
- **Student number:** n11572833
- **Application name:** Video Transcoder 
- **Two line description:** This REST API uploads a video and transcodes it from a .mov format to mp4 format.


Core criteria
------------------------------------------------

### Containerise the app

- **ECR Repository name:** a1lahan
- **Video timestamp:** 00.04
- **Relevant files:**
    - /Dockerfile

### Deploy the container

- **EC2 instance ID:** i-0f0c3e77813465b9e
- **Video timestamp:** 00.09

### User login

- **One line description:** Hard-coded username password for api.
- **Video timestamp:** 00.32
- **Relevant files:** 
    - /userData.json

### REST API

- **One line description:** REST API with endpoints- Register, Login, Transcode, Jobstatus and HTTP methods (GET, POST, PUT, DELETE)
- **Video timestamp:** 00.26
- **Relevant files:**
    - routes/auth.js
    - routes/transcode.js

### Data types

- **One line description:** used json file to store userid and password as structured data and uploaded and transcoded video is an .mov file and mp4 file which are unstructred data.
- **Video timestamp:**
- **Relevant files:**
    - 

#### First kind

- **One line description:** Video files
- **Type:** unstructured
- **Rationale:** Video files are large for database. stored locally
- **Video timestamp:** 01:09
- **Relevant files:**
    - /userData.json

#### Second kind

- **One line description:** userid and password stored in json file
- **Type:** structured
- **Rationale:**  Need to be able to query for regiser and login endpoints
- **Video timestamp:** 01:24
- **Relevant files:**
  - /uploads/5 Minute Timer.mov

### CPU intensive task

 **One line description:** converting a .mov video file to .mp4 file vide file
- **Video timestamp:** 01:35
- **Relevant files:**
    - 

### CPU load testing

 **One line description:** Node script to generate requests to stabilise endpoint
- **Video timestamp:** 01:55
- **Relevant files:**
    - 

Additional criteria
------------------------------------------------

### Extensive REST API features

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    - 

### External API(s)

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    - 

### Additional types of data

- **One line description:** log file showing transcoding process
- **Video timestamp:** 01:30
- **Relevant files:**
    - /transcode.log

### Custom processing

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    - 

### Infrastructure as code

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    - 

### Web client

- **One line description:**
- **Video timestamp:**
- **Relevant files:**
    -   

### Upon request

- **One line description:** Not attempted
- **Video timestamp:**
- **Relevant files:**
    - 