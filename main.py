from flask import Flask, redirect, render_template, request

from wanted_scraper import WantedScraper

app = Flask("JobScraper")


@app.route("/")
def home():
    return render_template("home.html", name="nico")


@app.route("/search")
def search():
    keyword = request.args.get("keyword")
    if keyword is None:
        return redirect("/")

    wanted_scraper = WantedScraper(keyword)
    wanted_scraper.search()

    return render_template(
        "search.html",
        search_results=wanted_scraper.search_results,
    )


app.run(host="127.0.0.1", port=5001, debug=True)

# from file import save_to_file
# from remote_scraper import RemoteScraper
# from wanted_scraper import WantedScraper

# if __name__ == "__main__":
#     # input = input("검색어를 입력하세요: ")

#     input = ["python", "nextjs", "react"]
#     for i in input:
#         scraper = WantedScraper(i)
#         scraper.search()
#         remote_scraper = RemoteScraper("remoteok", i)
#         remote_scraper.search()
#         remote_wework_scraper = RemoteScraper("weworkremotely", i)
#         remote_wework_scraper.search()
#         save_to_file(
#             i,
#             scraper.search_results
#             + remote_scraper.search_result
#             + remote_wework_scraper.search_result,
#         )
