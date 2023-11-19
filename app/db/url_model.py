from sqlmodel import SQLModel, Field

class VideoUrls(SQLModel, table=True):
    __tablename__ = "video_urls"
    url:str = Field(default=None, primary_key=True)
    