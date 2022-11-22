import asyncio
import json
import wave
import subprocess
import websockets


class AudioRecognizer:
    def recognize(self, audio):
        pass


class VoskAudioRecognizer(AudioRecognizer):
    def __init__(self, host):
        self._host = host
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._event_loop = asyncio.get_event_loop()

    def recognize(self, file_name):
        wav_path = "./" + file_name.split('.')[0] + ".wav"
        print(wav_path)
        # convert oog to wav
        command = f"ffmpeg -i {file_name} -ar 16000 -ac 2 -ab 192K -f wav {wav_path}"
        _ = subprocess.check_call(command.split())
        recognizer_results = self._event_loop.run_until_complete(
            self.send_audio_to_recognizer(file_name)
        )
        print(recognizer_results)

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
                if 'result' in json_data:
                    recognizer_results += json_data['result']

            await websocket.send('{"eof" : 1}')
            await websocket.recv()
            return recognizer_results
