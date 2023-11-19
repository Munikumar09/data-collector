from sqlmodel import Session, select
from app.db.connection import engine
from app.db.url_model import VideoUrls
from app.data_instances.video_meta import VideoMetaData
from app.db.video_metadata_model import VideoMetaDataModel
from typing import List, Optional


def filter_and_insert_videos(
    videos_metadata: List[VideoMetaData],
) -> List[VideoMetaData]:
    """
    Insert the video urls into the database that do not already exist in the database

    Parameters
    ----------
    videos_metadata: ``List[VideoMetaData]``
        A list of VideoMetaData objects for each video

    Returns
    -------
    ``List[VideoMetaData]``
        A list of VideoMetaData objects for each video that were inserted into the database
    """
    filtered_videos = []

    with Session(engine) as session:
        for video_metadata in videos_metadata:
            url_exists = session.exec(
                select(VideoUrls).where(VideoUrls.url == video_metadata.url)
            ).first()

            if url_exists:
                continue

            video_url = VideoUrls(url=video_metadata.url)
            session.add(video_url)
            filtered_videos.append(video_metadata)
        session.commit()

    return filtered_videos


def get_video_metadata(session: Session, video_id: str) -> Optional[VideoMetaDataModel]:
    """
    Retrieve the video metadata from the database for the given video id

    Parameters
    ----------
    session: ``Session``
        The database session
    video_id: ``str``
        The video id of the video to retrieve the metadata from the database

    Returns
    -------
    ``Optional[VideoMetaDataModel]``
        The video metadata for the given video id
    """
    statement = select(VideoMetaDataModel).where(
        VideoMetaDataModel.video_id == video_id
    )
    video_metadata = session.exec(statement).first()

    return video_metadata


def insert_video_metadata(video_metadata: VideoMetaData):
    """
    Insert the video metadata into the database if it does not already exist in the database

    Parameters
    ----------
    video_metadata: ``VideoMetaData``
        The video metadata to insert into the database
    """
    with Session(engine) as session:
        video_metadata_model = VideoMetaDataModel(**video_metadata.as_dict())
        video_metadata = get_video_metadata(session, video_metadata_model.video_id)
        
        if video_metadata:
            return
        
        session.add(video_metadata_model)
        session.commit()
