from __future__ import annotations

import json
import random
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENDPOINT = "http://localhost:9222"
BASE_RESUME = (ROOT / "data/resumes/product-management.pdf").resolve()
HELPER = ROOT / "src/job_application_automation/engines/ashby_raw_cdp.py"
URL_RE = re.compile(r"^https://jobs\.ashbyhq\.com/", re.I)


def jobs() -> list[dict[str, str]]:
    paths = [
        ROOT / "data/application-queues/ashby-job-search-2026-08-08.json",
        ROOT / "data/application-queues/ashby-job-search-2026-08-04.json",
    ]
    seen: set[str] = set()
    ordered: list[dict[str, str]] = []
    for path in paths:
        for raw in json.loads(path.read_text(encoding="utf-8")):
            url = str(raw.get("job_url") or raw.get("url") or "").strip()
            if not URL_RE.match(url) or url in seen:
                continue
            seen.add(url)
            ordered.append(
                {
                    "url": url,
                    "company": str(raw.get("company") or raw.get("company_name") or "Company"),
                    "title": str(raw.get("title") or raw.get("role") or "Role"),
                }
            )
    return ordered


def application_url(url: str) -> str:
    return url.rstrip("/") + ("" if url.rstrip("/").endswith("/application") else "/application")


def create_target(url: str, timeout: float) -> dict[str, str]:
    request = urllib.request.Request(
        ENDPOINT + "/json/new?" + urllib.parse.quote(url, safe=""), method="PUT"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def reload_target(target: dict[str, str], timeout: float = 3.0) -> None:
    from websockets.sync.client import connect

    websocket = connect(target["webSocketDebuggerUrl"], open_timeout=timeout, close_timeout=1)
    try:
        websocket.send(json.dumps({"id": 1, "method": "Page.reload", "params": {}}))
        websocket.recv(timeout=timeout)
    finally:
        websocket.close()


def normalized_words(value: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9]+", value.casefold()) if len(word) > 2]


def exact_resume(company: str, title: str) -> Path:
    company_words = normalized_words(company)
    title_words = normalized_words(title)
    matches: list[Path] = []
    for path in (ROOT / "output").glob("*Resume.pdf"):
        name = path.stem.casefold()
        if all(word in name for word in company_words) and all(word in name for word in title_words):
            matches.append(path)
    return max(matches, key=lambda path: path.stat().st_mtime).resolve() if matches else BASE_RESUME


def helper_command(target_id: str, job: dict[str, str], resume: Path, email: str) -> list[str]:
    values = {
        "name": "Shivam Singh",
        "first_name": "Shivam",
        "last_name": "Singh",
        "email": email,
        "phone": "6502833478",
        "location": "San Francisco, California, United States",
        "linkedin": "https://linkedin.com/in/beastofbayarea",
        "twitter": "https://x.com/BeastofBayArea",
    }
    answers = {
        "Are you authorized to work in the United States?": "Yes",
        "Are you legally authorized to work in the United States?": "Yes",
        "Will you now or in the future require sponsorship?": "No",
        "Will you now or in the future require sponsorship for employment visa status?": "No",
        "Are you comfortable working in US time zones?": "Yes",
    }
    return [
        sys.executable,
        str(HELPER),
        "--target-id",
        target_id,
        "--url",
        application_url(job["url"]),
        "--resume",
        str(resume),
        "--values-json",
        json.dumps(values),
        "--answers-json",
        json.dumps(answers),
        "--command-timeout",
        "5",
        "--render-timeout",
        "7",
    ]


def invoke(command: list[str], timeout: float) -> dict[str, object]:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=max(1.0, timeout),
        )
    except subprocess.TimeoutExpired:
        return {"success": False, "status": "HELPER_TIMEOUT", "errors": ["helper timeout"]}
    for line in completed.stdout.splitlines():
        if line.startswith("ASHBY_RAW_CDP_RESULT="):
            return json.loads(line.split("=", 1)[1])
    return {
        "success": False,
        "status": "HELPER_RESULT_MISSING",
        "errors": [(completed.stderr or completed.stdout)[-500:]],
    }


def main() -> int:
    queue = jobs()
    emails = json.loads((ROOT / "config/candidate_email_pool.json").read_text())
    indices = list(range(43, min(178, len(queue)) + 1, 3))
    totals = {"filled": 0, "partial": 0, "failed": 0}
    print(json.dumps({"event": "lane_start", "unique": len(queue), "indices": indices}), flush=True)
    for index in indices:
        started = time.monotonic()
        job = queue[index - 1]
        url = application_url(job["url"])
        email = random.choice(emails)
        resume = exact_resume(job["company"], job["title"])
        target: dict[str, str] | None = None
        result: dict[str, object] = {"success": False, "status": "TARGET_FAILED"}
        attempts: list[str] = []
        try:
            target = create_target(url, 5)
            result = invoke(helper_command(target["id"], job, resume, email), 24)
            attempts.append(str(result.get("status")))
            if not result.get("success") and time.monotonic() - started < 42:
                try:
                    reload_target(target)
                except Exception:
                    pass
                result = invoke(helper_command(target["id"], job, resume, email), 12)
                attempts.append("reload:" + str(result.get("status")))
            if not result.get("success") and time.monotonic() - started < 51:
                target = create_target(url, 4)
                result = invoke(
                    helper_command(target["id"], job, resume, email),
                    max(3, 58 - (time.monotonic() - started)),
                )
                attempts.append("reopen:" + str(result.get("status")))
        except Exception as exc:
            result = {"success": False, "status": type(exc).__name__, "errors": [str(exc)]}
        status = str(result.get("status", "FAILED"))
        if result.get("success"):
            totals["filled"] += 1
        elif status == "PARTIALLY_FILLED":
            totals["partial"] += 1
        else:
            totals["failed"] += 1
        print(
            json.dumps(
                {
                    "event": "job_result",
                    "index": index,
                    **job,
                    "target_id": target.get("id") if target else "",
                    "email": email,
                    "resume": str(resume),
                    "status": status,
                    "attached_files": result.get("attached_files", []),
                    "visible_files": result.get("visible_files", []),
                    "required_empty": result.get("required_empty", []),
                    "attempts": attempts,
                    "elapsed": round(time.monotonic() - started, 1),
                    "submitted": False,
                }
            ),
            flush=True,
        )
    print(json.dumps({"event": "lane_complete", **totals, "processed": len(indices)}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
