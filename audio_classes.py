import json


class RecognizedWord:
    def __init__(self, word, begin_timestamp, end_timestamp, probability):
        self.word = word
        self.start = begin_timestamp
        self.end = end_timestamp
        self.conf = probability

    def get_word(self):
        return self.word

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_probability(self):
        return self.conf


class RecognizedSentence:
    def __init__(self, json_file):
        self.words = []
        self.text = json_file['text']
        for i in json_file['result']:
            self.add_word(i['word'], i['start'], i['end'], i['conf'])

    def add_word(self, word, start, end, conf):
        self.words.append(RecognizedWord(word, start, end, conf))

    def generate_output_info(self):
        answer = f"Полученное предложение: \n{self.text}\nСтатистика по сообщению:\n"
        for i in self.words:
            answer += f"Слово \"{i.get_word()}\" было сказано в промежутке {i.get_start()} - {i.get_end()} с " \
                      f"вероятностью {i.get_probability()}\n"
        return answer

