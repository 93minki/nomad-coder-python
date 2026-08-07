from flask import Flask, redirect, render_template, request, send_file

from file import save_to_file
from wanted_scraper import WantedScraper

app = Flask("JobScraper")

db = {"python": []}


@app.route("/")
def home():
    return render_template("home.html", name="nico")


@app.route("/search")
def search():
    keyword = request.args.get("keyword")

    if not keyword:
        return redirect("/")

    if keyword in db:
        jobs = db[keyword]
    else:
        wanted_scraper = WantedScraper(keyword)
        wanted_scraper.search()
        jobs = wanted_scraper.search_results
        db[keyword] = jobs

    return render_template(
        "search.html",
        search_results=jobs,
        keyword=keyword,
    )


@app.route("/export")
def export():
    keyword = request.args.get("keyword")
    if not keyword:
        return redirect("/")
    if keyword not in db:
        return redirect(f"/search?keyword={keyword}")

    save_to_file(keyword, db[keyword])
    return send_file(f"{keyword}.csv", as_attachment=True)


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
