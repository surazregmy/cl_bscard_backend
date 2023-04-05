import boto3


class Storage:
	def __init__(self, storage_location, access_key_id, secret_access_key):
		self.client = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
		self.bucket_name = storage_location

	def get_storage_location(self):
		return self.bucket_name

	def upload_file(self, file_bytes, file_name):
		self.client.put_object(Bucket=self.bucket_name, Body=file_bytes, Key=file_name, ACL='public-read')

		return {'fileId': file_name, 'fileUrl': 'https://' + self.bucket_name + '.s3.amazonaws.com/' + file_name}