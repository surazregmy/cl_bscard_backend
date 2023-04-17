import json, base64
from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import comprehend_service
from chalicelib import dynamoDB
from chalicelib import iam

# APP Initialization
app = Chalice(app_name='Business Contacts')
app.debug = True


## Initialize AWS Services
storage_location = 'contentcen301217943.aws.ai'
storage_service = storage_service.StorageService(storage_location)
iam = iam.IAMService()
recognition_service = recognition_service.RecognitionService(storage_service)
comprehend_service = comprehend_service.ComprehendService()
db = dynamoDB.DynamoDBService()


#upload a single image to AWS bucket
@app.route('/api/images', methods=['POST'], cors=True)
def upload_image():
	request_data = json.loads(app.current_request.raw_body)
	file_name = request_data['filename']
	file_bytes = base64.b64decode(request_data['filebytes'])
	image_info = storage_service.upload_file(file_bytes, file_name)
	return image_info


@app.route('/api/images/{image_id}/detect-field', methods=['GET'], cors=True)
def detect_text(image_id):
	# image to text and extract Personally identifiable information
	card = recognition_service.detect_text(image_id)
	if isinstance(card, dict):
		return card
	pii = comprehend_service.detect_comprehend(card)
	phi = comprehend_service.detect_medicalcomprehend(card)
	return {
				'name': pii['NAME'] if 'NAME' in pii.keys() else None,
				'phone': pii['PHONE'] if 'PHONE' in pii.keys() else None,
				'email': phi['EMAIL'] if 'EMAIL' in phi.keys() else None,
				'website': phi['URL'] if 'URL' in phi.keys() else None,
				'address': pii['ADDRESS'] if 'ADDRESS' in pii.keys() else None
			}


@app.route('/api/cards/{image_id}/save-field', methods=['POST'], cors=True)
def save_text(image_id):
	# upload an item
	# format of request body {name: '', phone: '', email: '', website: '', address: ''}
	print("In the save_text")
	request_data = json.loads(app.current_request.raw_body)
	print("In the save_text 2")
	item = {
		'id': image_id,
		'username': request_data['name'],
		'phone': request_data['phone'],
		'email': request_data['email'],
		'website': request_data['website'],
		'address': request_data['address'],
		'access_id': request_data['access_id']
	}
	return db.insert_item(item)

@app.route('/api/cards/{access_id}', methods=['GET'], cors=True)
def get_all_cards(access_id):
	# get all business cards
	return db.find_items_by_access_id(access_id)


@app.route('/api/cards/{access_id}/search-text', methods=['POST'], cors=True)
def find_text(access_id):
	# find an item by name
	# format of request body {name: ''}
	request_data = json.loads(app.current_request.raw_body)
	return db.find_items_by_access_id_and_name(access_id, request_data['name'])

@app.route('/api/cards/{image_id}/{access_id}/update-field', methods=['PUT'], cors=True)
def update_text(image_id, access_id):
	
	request_data = json.loads(app.current_request.raw_body)
	item = db.find_id(image_id)
	if 'warning' in item.keys():
		return item
	# access control
	if access_id == item['access_id']:
		item = {
			'id': image_id,
			'name': request_data['name'],
			'phone': request_data['phone'],
			'email': request_data['email'],
			'website': request_data['website'],
			'address': request_data['address']
		}
		return db.update_item(item)
	else:
		return {'error': 'permission denied'}


@app.route('/api/cards/{image_id}/{access_id}/delete-card', methods=['DELETE'], cors=True)
def delete_text(image_id, access_id):
	# delete an card
	item = db.find_id(image_id)
	if 'warning' in item.keys():
		return item
	# check if the permission exists
	if access_id == item['access_id']:
		return db.delete_item(image_id)
	else:
		return {'error': 'permission denied'}
	

@app.route('/api/signup', methods=['POST'], cors=True)
def signup():
	request_data = json.loads(app.current_request.raw_body)
	
	a = db.find_user_by_email_and_password(request_data['email'],request_data['password'])
	if(a):
		return {'code':'400','error': 'User already exists'}
	iamuser = iam.create_user(request_data['email'].replace(' ', '-'))
	user = {
		'email': request_data['email'],
		'password': request_data['password'],
		'access_id':iamuser['access_id'],
	}
	return  db.insert_user(user)

@app.route('/api/login', methods=['POST'], cors=True)
def login():
	request_data = json.loads(app.current_request.raw_body)
	user = {
		'email': request_data['email'],
		'password': request_data['password'],
	}
	a = db.find_user_by_email_and_password(request_data['email'],request_data['password'])
	if(a is None):
		return {'code':'400','error': 'User donot exists'}
	return  db.find_user_by_email_and_password(request_data['email'],request_data['password'])
	
	