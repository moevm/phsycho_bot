import asyncio
import json
import logging
import wave
import subprocess
import websockets
import soundfile as sf


class Word:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return json.dumps({
            'value': self.value
        }, ensure_ascii=False)

    @staticmethod
    def from_json_string(json_string):
        json_obj = json.loads(json_string)
        return Word(value=json_obj['value'])


class RecognizedWord:
    def __init__(self, word, begin_timestamp, end_timestamp, probability):
        self.word = word
        self.begin_timestamp = begin_timestamp
        self.end_timestamp = end_timestamp
        self.probability = probability

    def __repr__(self):
        return json.dumps({
            'word': repr(self.word),
            'begin_timestamp': self.begin_timestamp,
            'end_timestamp': self.end_timestamp,
            'probability': self.probability
        }, ensure_ascii=False)

    @staticmethod
    def from_json_string(json_string):
        json_obj = json.loads(json_string)
        return RecognizedWord(
            Word.from_json_string(json_obj['word']),
            float(json_obj['begin_timestamp']),
            float(json_obj['end_timestamp']),
            float(json_obj['probability']),
        )


class AudioRecognizer:
    def recognize(self, audio):
        pass


class VoskAudioRecognizer(AudioRecognizer):
    def __init__(self, host):
        self._host = host
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._event_loop = asyncio.get_event_loop()

    def parse_recognizer_result(self, recognizer_result):
        return RecognizedWord(
            word=Word(recognizer_result['word']),
            begin_timestamp=recognizer_result['start'],
            end_timestamp=recognizer_result['end'],
            probability=recognizer_result['conf'],
        )

    def recognize(self, file_name):
        wav_path = "./" + file_name.split('.')[0] + ".wav"
        # convert oog to wav
        command = f"ffmpeg -i {file_name} -ar 16000 -ac 1 -ab 256K -f wav {wav_path}"
        _ = subprocess.check_call(command.split())

        # wav_path = 'file.wav'
        recognizer_results = self._event_loop.run_until_complete(
            self.send_audio_to_recognizer(wav_path)
        )
        # recognized_words = list(map(self.parse_recognizer_result, recognizer_results))
        return recognizer_results

    async def send_audio_to_recognizer(self, file_name):
        recognizer_results = []
        async with websockets.connect(self._host) as websocket:
            wf = wave.open(file_name, "rb")
            await websocket.send('''{"config" : { "sample_rate" : 8000.0 }}''')
            while True:
                data = wf.readframes(1000)
                if len(data) == 0:
                    break
                await websocket.send(data)
                json_data = json.loads(await websocket.recv())
                logging.info(json_data)
                if 'result' in json_data:
                    recognizer_results += json_data['result']

            await websocket.send('{"eof" : 1}')
            await websocket.recv()
            return recognizer_results
