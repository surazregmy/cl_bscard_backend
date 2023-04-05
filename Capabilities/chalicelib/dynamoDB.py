import boto3
from fuzzywuzzy import fuzz


class DynamoDBService:
	def __init__(self):
		dynamodb = boto3.resource('dynamodb')
		self.table = dynamodb.Table('carddatabase')

	def insert_item(self, item: dict):
		return self.table.put_item(Item=item)

	def find_id(self, item_id: str):
		result = self.table.get_item(Key={'id': item_id})
		return result['Item'] if 'Item' in result.keys() else {'warning': 'no such item in db'}
	
	def find_item_all(self):
		response = self.table.scan()
		result = list()
		for item in response['Items']:
				result.append(item)
		return result if result else {'warning': 'no data in table'}

	def find_item(self, name: str):
		response = self.table.scan()
		result = list()
		for item in response['Items']:
			if fuzz.token_set_ratio(name.lower(), item['username'].lower()) > 50:
				result.append(item)
		return result if result else {'warning': 'no such item in db'}

	def update_item(self, item: dict):
		response = self.table.update_item(
			Key={'id': item['id']},
			UpdateExpression='set username=:n, phone=:p, email=:e, website=:w, address=:a',
			ExpressionAttributeValues={
				':n': item['name'] if 'name' in item.keys() else None,
				':p': item['phone'] if 'phone' in item.keys() else None,
				':e': item['email'] if 'email' in item.keys() else None,
				':w': item['website'] if 'website' in item.keys() else None,
				':a': item['address'] if 'address' in item.keys() else None
			},
			ReturnValues='UPDATED_NEW'
		)
		return response

	def delete_item(self, item_id: str):
		return self.table.delete_item(Key={'id': item_id})