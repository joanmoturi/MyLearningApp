"""Bounded public-page observations; no credentials, private data or sentiment inference."""

import concurrent.futures
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

from build_course import COMPANIES, EXTRA_SOURCES, GUIDES, REPORTS, RESOURCE_SPECS, ROOT


def observe(url):
    request = urllib.request.Request(url, headers={"User-Agent": "EngineeringAcademy-source-verification/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read(180000).decode("utf-8", errors="replace")
            title = re.search(r"<title[^>]*>(.*?)</title>", body, re.IGNORECASE | re.DOTALL)
            return url, {
                "status": response.status, "final_url": response.url,
                "page_title": re.sub(r"\s+", " ", title.group(1)).strip()[:250] if title else None,
                "checked_at": datetime.now(UTC).isoformat(),
                "scope": "Bounded public HTTP response and title only; not vacancy, interview-policy or full video verification.",
            }
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return url, {"status": getattr(error, "code", None), "page_title": None,
                     "checked_at": datetime.now(UTC).isoformat(),
                     "scope": "Direct access unavailable; no content or eligibility inferred."}


if __name__ == "__main__":
    urls = {row[3] for row in COMPANIES} | {row[3] for row in RESOURCE_SPECS}
    urls.update(row[0] for row in GUIDES.values())
    urls.update(row[1] for row in REPORTS)
    urls.update(row[1] for row in EXTRA_SOURCES)
    urls.update({
        "https://www.hackerrank.com/interview/preparation-kits",
        "https://leetcode.com/studyplan/top-interview-150/",
    })
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = dict(pool.map(observe, sorted(urls)))
    for _, _, _, url, kind in RESOURCE_SPECS:
        if kind != "youtube_video":
            continue
        endpoint = "https://www.youtube.com/oembed?" + urllib.parse.urlencode({"url":url,"format":"json"})
        try:
            with urllib.request.urlopen(endpoint,timeout=15) as response:
                data=json.loads(response.read(50000))
            results[url]["oembed"]={"title":data.get("title"),"author_name":data.get("author_name"),
                                   "provider_name":data.get("provider_name"),
                                   "scope":"Official public oEmbed metadata; not duration, publication date, comments or complete playback."}
        except (urllib.error.URLError,TimeoutError,OSError,ValueError):
            results[url]["oembed"]={"scope":"Public oEmbed unavailable; no metadata invented."}
    (ROOT / "DSA_URL_VERIFICATION.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"Observed {len(results)} public URLs; {sum(r['status'] == 200 for r in results.values())} HTTP 200 responses. Other access remains unknown.")
