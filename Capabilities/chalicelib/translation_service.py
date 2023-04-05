import boto3

class TranslationService:
    def __init__(self):
        self.client = boto3.client('translate')

    def translate_text(self, text, source_language = 'auto', target_language = 'en'):
        try:
            response = self.client.translate_text(
                Text = text,
                SourceLanguageCode = source_language,
                TargetLanguageCode = target_language
            )
            translation = {
                'sourceText':text,
                'translatedText': response['TranslatedText'],
                'sourceLanguage': response['SourceLanguageCode'],
                'targetLanguage': response['TargetLanguageCode']
            }
            return translation
        except self.client.UnsupportedLanguagePairException:
            translation = {
                'sourceText':text,
                'translatedText': "Langaue is not Supported",
                'sourceLanguage': "Unsupported Langauge",
                'targetLanguage': "Translation is not supported for this Langauge"
            }
            return translation

            




