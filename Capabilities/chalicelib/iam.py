import boto3


class IAMService:
	def __init__(self):
		self.iam = boto3.client('iam')

	def create_user(self, username: str):
		for user in self.iam.list_users(PathPrefix='/dynamodb/modify/')['Users']:
			if user['UserName'] == username:
				self.iam.delete_user(UserName=username)
		response = self.iam.create_user(Path='/dynamodb/modify/', UserName=username)
		return {'iam-user': response['User']['UserName'], 'access_id': response['User']['UserId']}

	def delete_user(self, username: str):
		self.iam.delete_user(UserName=username)