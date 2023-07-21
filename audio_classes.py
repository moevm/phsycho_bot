from dataclasses import dataclass


@dataclass(frozen=True)
class RecognizedWord:
    word: str
    begin_timestamp: float
    end_timestamp: float
    probability: float


class RecognizedSentence:
    def __init__(self, json_file):
        self._words = []
        self._text = json_file['text']
        for segment in json_file['segments']:
            for i in segment['words']:
                self.__add_word(i['word'], i['start'], i['end'], i['probability'])

    def __add_word(self, word, start, end, conf):
        self._words.append(RecognizedWord(word, float(start), float(end), float(conf)))

    def generate_output_info(self):
        answer_list = [f"Полученное предложение: \n{self._text}\nСтатистика по сообщению:\n"]
        for i in self._words:
            answer_list.append(
                f"Слово \"{i.word}\" было сказано в промежутке {i.begin_timestamp} - {i.end_timestamp} с "
                f"вероятностью {i.probability}\n"
            )
        return "".join(answer_list)

    def generate_stats(self):
        return '\n'.join([f"{i.word} - {i.begin_timestamp} - {i.end_timestamp} - {i.probability}" for i in self._words])
