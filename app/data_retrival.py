from youtubesearchpython import CustomSearch
from youtube_transcript_api import YouTubeTranscriptApi


class DataRetrieval:
    def get_video_urls_with_query(self, query, max_pages=1):
        # Define the search query
        search_query = query.replace(" ", "+")

        # Create a CustomSearch object with the filter parameter
        custom_search = CustomSearch(
            search_query,
            searchPreferences="EgQoATAB",
        )
        urls = []
        for _ in range(max_pages):
            for results in custom_search.result()["result"]:
                urls.append(results["link"])
            custom_search.next()
        return urls

    def get_video_transcript(self, url):
        video_id = url.split("=")[1]
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_manually_created_transcript(["hi"])
            return transcript.fetch()
        except Exception as e:
            return None
