import boto3


class IAM:
	def __init__(self, access_key_id, secret_access_key):
		self.iam = boto3.client('iam', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)

	def create_user(self, username: str):
		for user in self.iam.list_users(PathPrefix='/dynamodb/modify/')['Users']:
			if user['UserName'] == username:
				self.iam.delete_user(UserName=username)
		response = self.iam.create_user(Path='/dynamodb/modify/', UserName=username)
		return {'iam-user': response['User']['UserName'], 'access_id': response['User']['UserId']}

	def delete_user(self, username: str):
		self.iam.delete_user(UserName=username)