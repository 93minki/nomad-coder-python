from pydantic import BaseModel


class Job(BaseModel):
    title: str | None = None
    company_name: str | None = None
    url: str | None = None  # wanted의 link
    location: str | list[str] | None = None  # wework의 company_hq, remoteok의 location
    tags: list[str] | None = None  # wework의 categories, remoteok의 tags
    experience: str | None = None  # wanted only
    reward: str | None = None  # wanted only
