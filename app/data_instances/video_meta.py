from dataclasses import dataclass


@dataclass
class VideoMetaData:
    video_id: str
    url: str
    title: str
    duration: int
    published_time: str
    channel_name: str
    published_year: str

    def as_dict(self):
        return {
            "video_id": self.video_id,
            "url": self.url,
            "title": self.title,
            "duration": self.duration,
            "published_time": self.published_time,
            "channel_name": self.channel_name,
            "published_year": self.published_year,
        }
