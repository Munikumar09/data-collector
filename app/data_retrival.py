from typing import List
from youtubesearchpython import CustomSearch
from youtube_transcript_api import YouTubeTranscriptApi
from app.data_instances.video_meta import VideoMetaData
from app.utils.date_utils import get_date_with_duration, duration_to_seconds
from tqdm import tqdm


class DataRetrieval:
    def get_video_metadata_with_query(
        self, search_query: str, max_pages: int = 1
    ) -> List[VideoMetaData]:
        """
        Get the metadata of the videos with the given query string and max_pages

        Parameters
        ----------
        search_query: ``str``
            The query string to search for videos on YouTube
        max_pages: ``int``
            The maximum number of pages to search for videos. Each page has 20 videos.

        Returns
        -------
        List[VideoMetaData]
            A list of VideoMetaData objects for each video
        """
        search_query = search_query.replace(" ", "+")
        videos_metadata: List[VideoMetaData] = []
        custom_search = CustomSearch(
            search_query,
            searchPreferences="EgQoATAB",
        )
        
        for _ in range(max_pages):
            results = custom_search.result()
            video_metadata = self._extract_video_metadata(results)
            videos_metadata.extend(video_metadata)
            custom_search.next()

        return videos_metadata

    def _extract_video_metadata(self, results) -> List[VideoMetaData]:
        """
        Extract the video metadata from the results of the search query

        Parameters
        ----------
        results: ``dict``
            The results of the search query from the YouTube API

        Returns
        -------
        ``List[VideoMetaData]``
            A list of VideoMetaData objects for each video
        """
        video_metadata: List[VideoMetaData] = []

        for result in results["result"]:
            try:
                video_id = result["id"]
                url = result["link"]
                title = result["title"]
                duration = duration_to_seconds(result["duration"])
                published_time = result["publishedTime"]
                published_year = get_date_with_duration(result["publishedTime"])
                channel_name = result["channel"]["name"]

                video_meta_data = VideoMetaData(
                    video_id=video_id,
                    url=url,
                    title=title,
                    duration=duration,
                    published_time=published_time,
                    published_year=published_year,
                    channel_name=channel_name,
                )
                video_metadata.append(video_meta_data)
                
            except Exception as e:
                pass

        return video_metadata

    def get_video_transcripts(self, videos_metadata: List[VideoMetaData]):
        """
        Get the video transcript for the given list of videos metadata

        Parameters
        ----------
        videos_metadata: ``List[VideoMetaData]``
            A list of VideoMetaData objects for each video

        Returns
        -------
        ``dict``
            A dictionary of video transcript for each video
        """
        video_transcription_data = {}
        
        for video_metadata in tqdm(videos_metadata):
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(
                    video_metadata.video_id
                )
                transcript = transcript_list.find_manually_created_transcript(["hi"])
                video_transcription_data[video_metadata.url] = transcript.fetch()
            except Exception as e:
                pass
            
        return video_transcription_data
