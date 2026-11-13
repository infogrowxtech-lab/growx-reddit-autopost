"""Growx Tech IT - Reddit auto poster (runs on GitHub Actions, free).

Each run (3 slots a day) decides whether to post, so the day ends with 1-3 posts.
First 14 days: max 1 post/day (new-account safety).
Posts are taken from queue/ in filename order. Delete or edit a file there to skip/change it.
Create a file named PAUSE in the repo root to stop all posting.
"""
import datetime as dt
import json
import os
import random
import shutil
import sys
from pathlib import Path

import praw

ROOT = Path(__file__).parent
QUEUE, POSTED, FAILED = ROOT / "queue", ROOT / "posted", ROOT / "failed"
STATE = ROOT / "state.json"
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
SLOTS = 3
WARMUP_DAYS = 14


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def parse_post(path):
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    if text.startswith("---"):
        _, head, body = text.split("---", 2)
        for line in head.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body.strip()


def submit(reddit, path):
    meta, body = parse_post(path)
    sub = reddit.subreddit(meta["subreddit"].replace("r/", ""))
    flair_id = None
    want = meta.get("flair", "").lower()
    if want:
        try:
            for f in sub.flair.link_templates.user_selectable():
                if want in f["flair_text"].lower():
                    flair_id = f["flair_template_id"]
                    break
        except Exception:
            pass
    post = sub.submit(title=meta["title"], selftext=body, flair_id=flair_id)
    return "https://reddit.com" + post.permalink


def main():
    force = os.environ.get("FORCE_POST") == "true"
    if (ROOT / "PAUSE").exists() and not force:
        print("PAUSE file found - skipping.")
        return

    now = dt.datetime.now(IST)
    today = now.date().isoformat()
    state = load_state()
    state.setdefault("start_date", today)
    if state.get("date") != today:
        age = (now.date() - dt.date.fromisoformat(state["start_date"])).days
        state.update(date=today, posted_today=0,
                     target=1 if age < WARMUP_DAYS else random.randint(1, 3))

    slot = 0 if now.hour < 12 else (1 if now.hour < 17 else 2)
    remaining_slots = SLOTS - slot
    need = state["target"] - state["posted_today"]

    should_post = force or (need > 0 and (need >= remaining_slots or random.random() < need / remaining_slots))
    print(f"{today} slot={slot} target={state['target']} posted={state['posted_today']} post_now={should_post}")

    if should_post:
        files = sorted(p for p in QUEUE.glob("*.md"))
        if not files:
            print("Queue empty - add more posts.")
        reddit = None
        for path in files[:3]:  # try up to 3 if one fails (e.g. subreddit rule)
            if reddit is None:
                reddit = praw.Reddit(
                    client_id=os.environ["REDDIT_CLIENT_ID"],
                    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                    username=os.environ["REDDIT_USERNAME"],
                    password=os.environ["REDDIT_PASSWORD"],
                    user_agent="growx-poster/1.0 by u/" + os.environ["REDDIT_USERNAME"],
                )
            try:
                url = submit(reddit, path)
                with path.open("a", encoding="utf-8") as f:
                    f.write(f"\n\n<!-- posted {now.isoformat()} {url} -->\n")
                shutil.move(str(path), POSTED / path.name)
                state["posted_today"] += 1
                print("Posted:", url)
                break
            except Exception as e:  # noqa: BLE001
                with path.open("a", encoding="utf-8") as f:
                    f.write(f"\n\n<!-- failed {now.isoformat()}: {e} -->\n")
                shutil.move(str(path), FAILED / path.name)
                print("Failed:", path.name, e, file=sys.stderr)

    STATE.write_text(json.dumps(state, indent=2))


if __name__ == "__main__":
    main()
