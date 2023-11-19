import re
from typing import List, Dict, Optional


class DataValidator:
    def validate_transcription(
        self, transcriptions: List[Dict[str, str]]
    ) -> Optional[List[Dict[str, str]]]:
        """
        Validate the transcription of a video and return the valid transcription

        The transcriptions are validated based on the following criteria:
            1) The transcription should not be empty
            2) The transcription should not have more than 20% non-Hindi tokens

        Parameters
        ----------
        transcription: List[Dict[str, str]]
            A list of dictionaries containing text and time of the video

        Returns
        -------
        Optional[List[Dict[str, str]]]
            A list of dictionaries containing text and time of the video, or None if the transcription is invalid
        """

        if len(transcriptions) < 2:
            return None

        filtered_transcriptions = []
        non_hindi_tokens_len = 0
        total_len = 0

        for data in transcriptions:
            text = self.clean_text(data["text"])
            data["text"] = text

            if text.strip() == "":
                continue

            non_hindi_tokens_len += len(self.get_non_hindi_tokens(text))
            total_len += len(text.split())
            filtered_transcriptions.append(data)

        percent = (non_hindi_tokens_len / (total_len+1e-9)) * 100

        if percent > 20:
            return None

        return filtered_transcriptions

    def validate_transcriptions(
        self, video_transcription_data: Dict[str, List[Dict[str, str]]]
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Validate the transcriptions of the videos and return the valid transcriptions

        Parameters
        ----------
        video_transcription_data: Dict[str, List[Dict[str, str]]]
            A dictionary of video URL and its transcription

        Returns
        -------
        Dict[str, List[Dict[str, str]]]
            A dictionary of video URL and its valid transcription
        """
        valid_transcriptions = {}
        
        for video_url, transcription in video_transcription_data.items():
            clean_transcription = self.validate_transcription(transcription)
            
            if clean_transcription:
                valid_transcriptions[video_url] = clean_transcription

        return valid_transcriptions

    def get_non_hindi_tokens(self, text: str) -> List[str]:
        """
        Find the non-Hindi tokens in the given text

        Parameters
        ----------
        text: str
            The text to be processed

        Returns
        -------
        List[str]
            A list of non-Hindi tokens in the text
        """
        non_hindi_tokens = re.findall(r"[a-zA-Z]+", text)
        return non_hindi_tokens

    def clean_text(self, text: str) -> str:
        """
        Clean the text by replacing special characters and unwanted tokens

        Parameters
        ----------
        text: str
            The text to be cleaned

        Returns
        -------
        str
            The cleaned text
        """
        text = text.replace("\n", " ").replace("\xa0", "").replace("[संगीत]", " ")
        return text
