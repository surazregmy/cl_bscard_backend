import json, base64
from chalice import Chalice
from chalicelib import storage_service
from chalicelib import recognition_service
from chalicelib import comprehend_service
from chalicelib import dynamoDB
from chalicelib import iam

#####
# chalice app configuration
#####
app = Chalice(app_name='leads contact')
app.debug = True

#####
# services initialization
#####
access_key_id = 'aws access key'
secret_access_key = 'aws secret key'
storage_location = 'bucket name'
storage_service = storage_service.Storage(storage_location, access_key_id, secret_access_key)
recognition_service = recognition_service.Recognition(storage_service, access_key_id, secret_access_key)
comprehend_service = comprehend_service.Comprehend(access_key_id, secret_access_key)
db = dynamoDB.DB(access_key_id, secret_access_key)
iam = iam.IAM(access_key_id, secret_access_key)

####
# restful endpoints
####


@app.route('/images', methods=['POST'], cors=True)
def upload_image():
	# processes file upload and saves file to storage service
	request_data = json.loads(app.current_request.raw_body)
	file_name = request_data['filename']
	file_bytes = base64.b64decode(request_data['filebytes'])
	image_info = storage_service.upload_file(file_bytes, file_name)
	return image_info


@app.route('/images/{image_id}/detect-text', methods=['GET'], cors=True)
def detect_text(image_id):
	# image to text and extract Personally identifiable information
	card = recognition_service.detect_text(image_id)
	if isinstance(card, dict):
		return card
	pii = comprehend_service.detect_pii(card)
	phi = comprehend_service.detect_phi(card)
	return {
				'name': pii['NAME'] if 'NAME' in pii.keys() else None,
				'phone': pii['PHONE'] if 'PHONE' in pii.keys() else None,
				'email': phi['EMAIL'] if 'EMAIL' in phi.keys() else None,
				'website': phi['URL'] if 'URL' in phi.keys() else None,
				'address': pii['ADDRESS'] if 'ADDRESS' in pii.keys() else None
			}


@app.route('/contacts/{image_id}/save-text', methods=['POST'], cors=True)
def save_text(image_id):
	# upload an item
	# format of request body {name: '', phone: '', email: '', website: '', address: ''}
	request_data = json.loads(app.current_request.raw_body)
	user = iam.create_user(request_data['name'].replace(' ', '-'))
	item = {
		'id': image_id,
		'username': request_data['name'],
		'phone': request_data['phone'],
		'email': request_data['email'],
		'website': request_data['website'],
		'address': request_data['address'],
		'iam-user': user['iam-user'],
		'access_id': user['access_id']
	}
	db.insert_item(item)
	return {'access_id': user['access_id']}


@app.route('/contacts/find-text', methods=['POST'], cors=True)
def find_text():
	# find an item by name
	# format of request body {name: ''}
	request_data = json.loads(app.current_request.raw_body)
	return db.find_item(request_data['name'])


@app.route('/contacts/{image_id}/{access_id}/update-text', methods=['PUT'], cors=True)
def update_text(image_id, access_id):
	# update an item
	# format of request body {'name', 'phone', 'email', 'website', 'address'}
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


@app.route('/contacts/{image_id}/{access_id}/delete-text', methods=['DELETE'], cors=True)
def delete_text(image_id, access_id):
	# delete an item
	item = db.find_id(image_id)
	if 'warning' in item.keys():
		return item
	# access control
	if access_id == item['access_id']:
		iam.delete_user(item['iam-user'])
		return db.delete_item(image_id)
	else:
		return {'error': 'permission denied'}