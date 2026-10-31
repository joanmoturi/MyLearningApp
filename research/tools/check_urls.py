"""Bounded public URL access checks; no login, media scraping or restrictions bypass."""

import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(url):
    request = urllib.request.Request(url, headers={"User-Agent": "EngineeringAcademyResearch/1.0 (public URL availability check)"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            # Availability check only; never harvest page/media/user data.
            response.read(1)
            return {"url": url, "http_status": response.status, "final_url": response.url, "access_status": "reachable", "error": None}
    except urllib.error.HTTPError as error:
        return {"url": url, "http_status": error.code, "final_url": error.url, "access_status": "blocked_or_unavailable", "error": str(error)}
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return {"url": url, "http_status": None, "final_url": None, "access_status": "network_error", "error": str(error)}


def run():
    register = json.loads((ROOT / "SOURCE_REGISTER.json").read_text(encoding="utf-8"))
    employers = json.loads((ROOT / "EMPLOYER_RESEARCH.json").read_text(encoding="utf-8"))
    # Verify YouTube video identities with official public oEmbed, not automated
    # watch-page scraping. Never attempt another route after denial.
    oembed_by_key = {
        s["id"].removeprefix("source-oembed-"): s["url"]
        for s in register["sources"] if s["source_type"] == "youtube_oembed"
    }
    targets = {
        s["id"]: oembed_by_key[s["id"].removeprefix("source-video-")] if s["source_type"] == "youtube" else s["url"]
        for s in register["sources"]
    }
    targets.update({"portal-" + e["id"]: e["career_url"] for e in employers["employers"]})
    urls = sorted(set(targets.values()))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = dict(zip(urls, pool.map(check, urls)))
    checked_at = datetime.now(timezone.utc).isoformat()
    for s in register["sources"]:
        result = results[targets[s["id"]]]
        s["http_status"] = result["http_status"]
        s["final_url"] = result["final_url"]
        s["url_last_checked_at"] = checked_at[:10]
    (ROOT / "SOURCE_REGISTER.json").write_text(json.dumps(register, indent=2) + "\n", encoding="utf-8")
    records = [{"entity_id": key, "verification_target": target, **results[target]} for key, target in targets.items()]
    report = {
        "checked_at": checked_at, "unique_requests": len(urls), "method": "One ordinary public GET per unique URL, bounded to 25 seconds; official oEmbed for YouTube. No retries or alternate routes for denied endpoints.",
        "content_verification": "Separate earlier reviewed content evidence is preserved; HTTP 200 alone does not confirm course completeness, job availability or free runtime.",
        "reachable_count": sum(r["access_status"] == "reachable" for r in results.values()),
        "unavailable_count": sum(r["access_status"] != "reachable" for r in results.values()),
        "results": records,
    }
    (ROOT / "URL_CHECK_RESULTS.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"URL checks: {report['reachable_count']} reachable / {len(urls)} unique requests; {report['unavailable_count']} blocked/unavailable. No denied access bypassed.")


if __name__ == "__main__":
    run()
