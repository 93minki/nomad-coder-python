import csv

from job import Job


def save_to_file(file_name, jobs: list[Job]):
    with open(f"{file_name}.csv", "w") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["title", "company_name", "url", "location", "tags", "experience", "reward"]
        )
        for job in jobs:
            writer.writerow(
                [
                    job.title,
                    job.company_name,
                    job.url,
                    job.location,
                    job.tags,
                    job.experience,
                    job.reward,
                ]
            )
