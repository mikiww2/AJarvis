#Ajarvis

##API: 
violetto-Ajarvis
authorizer: violetto-Ajarvis-authorizer

##S3:
bucket: violetto-stage

##IAM:
role: violetto-Ajarvis-lambda-authorizer
role: violetto-Ajarvis-lambda-retrieve
role: violetto-Ajarvis-lambda-scheduled-manager
role: violetto-Ajarvis-lambda-transcriber
role: violetto-Ajarvis-lambda-upload
role: violetto-Ajarvis-lambda-analyzer
role: violetto-Ajarvis-lambda-upload-text
role: violetto-Ajarvis-lambda-project
role: violetto-Ajarvis-lambda-download-audio

policy: violetto-Ajarvis-get-users
policy: violetto-Ajarvis-write-logs
policy: violetto-Ajarvis-s3-write
policy: violetto-Ajarvis-scan-transcription-jobs
policy: violetto-Ajarvis-start-transcription-job
policy: violetto-Ajarvis-get-transcription-job
policy: violetto-Ajarvis-get-audio
policy: violetto-Ajarvis-get-transcription-job-table
policy: violetto-Ajarvis-update-transcription-job
policy: violetto-Ajarvis-put-standup
policy: violetto-Ajarvis-delete-transcription-job
policy: violetto-Ajarvis-scan-standup-table
policy: violetto-Ajarvis-query-standup-table
policy: violetto-Ajarvis-get-standup-table
policy: violetto-Ajarvis-put-transcription-job-table
policy: violetto-Ajarvis-comprehend
policy: violetto-Ajarvis-get-transcribe-json
policy: violetto-Ajarvis-update-standups
policy: violetto-Ajarvis-get-comprehend-json

##DynamoDB:
table: violetto-Ajarvis-users
table: violetto-Ajarvis-transcription-jobs
table: violetto-Ajarvis-standups

##Lambda:
violetto-Ajarvis-authorizer
violetto-Ajarvis-upload
violetto-Ajarvis-scheduled-manager
violetto-Ajarvis-retrieve
violetto-Ajarvis-transcriber
violetto-Ajarvis-analyzer
violetto-Ajarvis-upload-text
violetto-Ajarvis-project
violetto-Ajarvis-download-audio

##CloudWatch:
rule: violetto-Ajarvis-scheduled-check-transc
