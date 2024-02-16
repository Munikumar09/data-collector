from typing import List, Union, Dict, Any
import sys
from youtubesearchpython import CustomSearch
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import  TranscriptList
from app.data_instances.video_meta import VideoMetaData
from app.utils.date_utils import get_date_with_duration, duration_to_seconds
from tqdm import tqdm
from youtubesearchpython import Playlist, playlist_from_channel_id
import yt_dlp
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s:%(message)s",
)


class DataRetrieval:
    """
    DataRetrieval class to retrieve the video metadata and transcriptions from YouTube.
    """

    def get_license_info(self, url):
        # ℹ️ See help(yt_dlp.YoutubeDL) for a list of available options and public functions
        ydl_opts = {
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # ℹ️ ydl.sanitize_info makes the info json-serializable
            d = ydl.sanitize_info(info)
            if "license" in d:
                return d["license"]
            return None

    def get_video_metadata_with_channel_id(
        self, channel_id: str
    ) -> List[VideoMetaData]:
        """
        Get the metadata of the videos with the given channel id

        Parameters
        ----------
        channel_id: ``str``
            The channel id to search for videos on YouTube

        Returns
        -------
        ``List[VideoMetaData]``
            A list of VideoMetaData objects for each video

        """
        raw_video_data = []
        temp_storage = []
        video_ids = set()
        try:
            playlist = Playlist(playlist_from_channel_id(channel_id))

            while playlist.hasMoreVideos:
                raw_video_data.extend(playlist.videos)
                playlist.getNextVideos()
            logger.info(f"total videos found: {len(raw_video_data)}")

            for video_data in tqdm(raw_video_data):
                video_url = f"https://www.youtube.com/watch?v={video_data['id']}"

                if (
                    video_data["id"] not in video_ids
                    and self.get_license_info(video_url) is not None
                ):
                    video_data["link"] = video_url
                    temp_storage.append(video_data)

                video_ids.add(video_data["id"])

        except TypeError as type_error:
            logger.warning(
                f"Exception occurred while extracting video links: {type_error}"
            )
        except Exception as e:
            logger.warning(f"Exception occurred while extracting video links: {e}")

        return self._extract_video_metadata(temp_storage)

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
        videos_metadata: List[VideoMetaData] = []
        custom_search = CustomSearch(
            search_query,
            searchPreferences="EgQoATAB",
        )

        for _ in range(max_pages):
            try:
                results = custom_search.result()
                video_metadata = self._extract_video_metadata(results["result"])
                videos_metadata.extend(video_metadata)
                custom_search.next()
            except Exception as e:
                print(f"Exception occurred while extracting video links: {e}")

        return videos_metadata

    def _extract_video_metadata(
        self, results: List[Dict[str, Any]]
    ) -> List[VideoMetaData]:
        """
        Extract the video metadata from the results of the search query

        Parameters
        ----------
        results: ``List[Dict[str,Any]]``
            The results of the search query from the YouTube API

        Returns
        -------
        ``List[VideoMetaData]``
            A list of VideoMetaData objects for each video
        """
        video_metadata: List[VideoMetaData] = []

        for result in results:
            try:
                video_id = result["id"]
                url = result["link"]
                title = result["title"]
                duration = duration_to_seconds(result["duration"])
                published_time = (
                    result["publishedTime"]
                    if "publishedTime" in result
                    else "0 years ago"
                )
                published_year = get_date_with_duration(published_time)
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
                print(f"Exception occurred while extracting video metadata: {e}")

        return video_metadata

    def get_manually_created_transcription(self,transcript_list:TranscriptList):
        try:
            return transcript_list.find_manually_created_transcript(["hi"]).fetch()
        except:
            return None

    def get_auto_generated_transcription(self,transcript_list:TranscriptList):
        try:
            return transcript_list.find_generated_transcript(["hi"]).fetch()
        except:
            return None

    def get_video_transcripts(self, videos_metadata: List[Union[str, VideoMetaData]])-> Dict[str, Dict[str, Any]]:
        """
        Get the video transcript for the given list of videos metadata

        Parameters
        ----------
        videos_metadata: ``List[VideoMetaData]``
            A list of VideoMetaData objects for each video

        Returns
        -------
        video_transcription_data: ``Dict[str, Dict[str, Any]]``
            A dictionary containing the video url as key and the manual and auto generated transcriptions as values
        """
        video_transcription_data = {}
        video_urls: List[str] = []

        if videos_metadata and isinstance(videos_metadata[0], VideoMetaData):
            video_urls = [video_metadata.url for video_metadata in videos_metadata]
        else:
            video_urls = videos_metadata

        for video_url in tqdm(video_urls):
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(
                    video_url.split("=")[-1]
                )
                manual_transcript = self.get_manually_created_transcription(transcript_list)
                auto_transcript = self.get_auto_generated_transcription(transcript_list)

                video_transcription_data[video_url] = {
                    "manual": manual_transcript,
                    "auto": auto_transcript,
                }
            except Exception as e:
                continue

        return video_transcription_data
