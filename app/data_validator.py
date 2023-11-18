import re


class DataValidator:
    def validate_transcription(self, transcription):
        new_transcription = []
        if len(transcription) < 2:
            return None
        non_hindi_tokens_len = 0
        total_len = 0
        for data in transcription:
            text = data["text"]
            text = text.replace("\n", " ").replace("\xa0", "").replace("[संगीत]"," ")
            data["text"] = text
            if text.strip() == "":
                continue
            non_hindi_tokens = self.get_non_Hindi_tokens(text)
            non_hindi_tokens_len += len(non_hindi_tokens)
            total_len += len(text.split())
            new_transcription.append(data)
        percent = (non_hindi_tokens_len / total_len) * 100
        if percent > 20:
            return None
        return new_transcription

    def get_non_Hindi_tokens(self, text):
        non_hindi_tokens = re.findall(r"[a-zA-Z]+", text)
        return non_hindi_tokens
