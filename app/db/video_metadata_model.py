from sqlmodel import SQLModel, Field


class VideoMetaDataModel(SQLModel, table=True):
    __tablename__ = "video_metadata"
    video_id: str = Field(default=None, primary_key=True)
    url: str
    title: str
    duration: int
    published_time: str
    channel_name: str
    published_year: str
