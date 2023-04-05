import boto3


class ComprehendService:
	def __init__(self):
		self.comprehend = boto3.client('comprehend')
		self.medical = boto3.client('comprehendmedical')

	def detect_comprehend(self, text_line):
		text = str()
		for line in text_line:
			text += line['text'] + '\n'
		response = self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
		result = dict()
		for entity in response['Entities']:
			result[entity['Type']] = text[entity['BeginOffset']:entity['EndOffset']]
		return result

	def detect_medicalcomprehend(self, text_line):
		text = str()
		for line in text_line:
			text += line['text'] + '\n'
		response = self.medical.detect_phi(Text=text)
		result = dict()
		for entity in response['Entities']:
			result[entity['Type']] = text[entity['BeginOffset']:entity['EndOffset']]
		return result