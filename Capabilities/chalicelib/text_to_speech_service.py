import boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
import sys
import subprocess
from tempfile import gettempdir

class TextToSpeechService:
    def __init__(self):
        self.client = boto3.client('polly')

    def text_to_speech(self, text):
        try:
            response = self.client.synthesize_speech(
                Text = text,
                OutputFormat="mp3",
                VoiceId="Joanna"
            )
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output = os.path.join("/Users/surazregmy/myProjects/pythonProjects/cloudMachineLearning/ObjectDetector/Website/", "speech.mp3")
                try:
                    with open(output, "wb") as file:
                        file.write(stream.read())
                except IOError as error:
                    print(error)
        else:
            return "not done"

        return "done"
