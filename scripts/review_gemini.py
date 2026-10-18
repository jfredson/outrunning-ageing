#!/usr/bin/env python3
"""Send one review packet to Gemini and file its answer (docs/reviews/protocol.md, "Running").

    python3 scripts/review_gemini.py docs/reviews/packets/2026-10-17-cells-and-settings.md
    python3 scripts/review_gemini.py PACKET --model gemini-3.1-pro-preview --raw DIR --no-search

Reads the key from GEMINI_API_KEY in the environment (start the shell with `zsh -ic` or source
~/.zshrc first) and never prints or writes it. Calls the model named by --model through the
streaming endpoint, writing the answer to a .partial.txt file in the --raw folder as it arrives so a
dropped connection keeps what came before, with Google Search lookup on (unless --no-search) and the model's
thinking at its highest level if the API accepts the setting. Saves the raw reply as JSON in the
--raw folder (outside the repository by default: the session's scratch folder, or the current
folder), and writes the filed review to docs/reviews/<date>-<packet>-<model>.md in the form the
protocol asks for: the model line with the version string the API reported, the date, the mode,
the packet file, then the response verbatim. Refuses to overwrite a filed review.

Standard library only. Written 2026-10-17 for the first review; copied from The Quiet Galaxy's
scripts/review_gemini.py of the same date, with the header text changed to this site's records.
The streamed answer is also echoed to the terminal as it arrives, so the call runs in the foreground
with visible progress (the lesson of the sibling's run, where a background call lost an answer).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REVIEWS = ROOT / "docs" / "reviews"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse"


def call(model: str, prompt: str, key: str, search: bool, thinking: bool, partial: Path) -> dict:
    """Stream the model's answer, appending each piece of text to `partial` as it arrives so a
    dropped connection keeps what came before. Returns a reply in the shape of generateContent's:
    one candidate with the joined text, plus the version string, grounding and usage from the
    last pieces."""
    body: dict = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 1.0}}
    if thinking:
        body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "high"}
    if search:
        body["tools"] = [{"google_search": {}}]
    req = urllib.request.Request(ENDPOINT.format(model=model), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    last = ""
    for wait in (0, 60, 180):
        if wait:
            time.sleep(wait)
        try:
            reply = {"candidates": [{"content": {"parts": [{"text": ""}]}, "finishReason": None}]}
            text_parts: list[str] = []
            with urllib.request.urlopen(req, timeout=900) as r, partial.open("a") as out:
                out.write(f"\n\n==== attempt started {dt.datetime.now().isoformat(timespec='seconds')} ====\n")
                for raw_line in r:
                    line = raw_line.decode("utf-8", "ignore").strip()
                    if not line.startswith("data:"):
                        continue
                    chunk = json.loads(line[5:].strip())
                    for key_ in ("modelVersion", "usageMetadata", "promptFeedback", "responseId"):
                        if key_ in chunk:
                            reply[key_] = chunk[key_]
                    for cand in chunk.get("candidates") or []:
                        for part in cand.get("content", {}).get("parts", []):
                            if part.get("thought"):
                                continue
                            t = part.get("text", "")
                            if t:
                                text_parts.append(t)
                                out.write(t)
                                out.flush()
                                sys.stdout.write(t)
                                sys.stdout.flush()
                        if cand.get("finishReason"):
                            reply["candidates"][0]["finishReason"] = cand["finishReason"]
                        if cand.get("groundingMetadata"):
                            gm = reply["candidates"][0].setdefault("groundingMetadata", {})
                            q = gm.setdefault("webSearchQueries", [])
                            for s_ in cand["groundingMetadata"].get("webSearchQueries") or []:
                                if s_ not in q:
                                    q.append(s_)
            reply["candidates"][0]["content"]["parts"][0]["text"] = "".join(text_parts)
            return reply
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:400]
            if e.code == 400 and thinking and "thinking" in detail.lower():
                print("the API refused the thinking setting; calling again without it", file=sys.stderr)
                return call(model, prompt, key, search, False, partial)
            if e.code in (429, 500, 503):
                last = f"HTTP {e.code}: {detail}"
                continue
            raise SystemExit(f"stopped: HTTP {e.code} from the Gemini API: {detail}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = f"connection problem: {e}"
            continue
    raise SystemExit(f"stopped: the Gemini API kept refusing or timing out after two back-offs (last: {last})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("packet", type=Path)
    ap.add_argument("--model", default="gemini-3.1-pro-preview")
    ap.add_argument("--raw", type=Path, default=Path(os.environ.get("REVIEW_RAW_DIR", ".")))
    ap.add_argument("--no-search", action="store_true")
    ap.add_argument("--no-thinking", action="store_true")
    args = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("stopped: GEMINI_API_KEY is not set in this shell")
    prompt = args.packet.read_text()
    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md$", args.packet.name)
    if not m:
        raise SystemExit("stopped: the packet file must be named YYYY-MM-DD-<packet>.md")
    packet_date, packet_name = m.groups()
    today = dt.datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    model_slug = args.model.replace(".", "-")
    out = REVIEWS / f"{today}-{packet_name}-{model_slug}.md"
    if out.exists():
        raise SystemExit(f"stopped: {out.relative_to(ROOT)} is already filed and is never edited")

    args.raw.mkdir(parents=True, exist_ok=True)
    partial = args.raw / f"{today}-{packet_name}-{model_slug}.partial.txt"
    started = time.time()
    reply = call(args.model, prompt, key, not args.no_search, not args.no_thinking, partial)
    took = time.time() - started

    raw_path = args.raw / f"{today}-{packet_name}-{model_slug}.json"
    raw_path.write_text(json.dumps(reply, indent=1))

    version = reply.get("modelVersion") or args.model
    cands = reply.get("candidates") or []
    if not cands:
        raise SystemExit(f"stopped: no answer in the reply (saved at {raw_path}); feedback: {reply.get('promptFeedback')}")
    cand = cands[0]
    text = "\n".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
    finish = cand.get("finishReason")
    grounding = cand.get("groundingMetadata") or {}
    queries = grounding.get("webSearchQueries") or []
    usage = reply.get("usageMetadata") or {}

    if args.no_search:
        mode = "the packet shown in full; lookup off"
    else:
        mode = (f"the packet shown in full; Google Search lookup on, {len(queries)} search"
                f"{'es' if len(queries) != 1 else ''} made" + (": " + "; ".join(queries) if queries else ""))
    header = (
        f"# Review: {packet_name} packet, {args.model}, {today}\n\n"
        f"Model: `{args.model}`, version string reported by the API `{version}`"
        f"{'' if args.no_thinking else ', thinking at the highest level the API allows'}. "
        f"Date: {today}. Mode: {mode}. Called through the Gemini API by `scripts/review_gemini.py` "
        f"and filed verbatim the same day. Finish reason: {finish}. Tokens: {usage.get('promptTokenCount', '?')} in, "
        f"{usage.get('candidatesTokenCount', '?')} out, {usage.get('thoughtsTokenCount', 0)} thinking; "
        f"{took:.0f} seconds. Never edited after filing.\n\n"
        f"Packet sent: `docs/reviews/packets/{packet_date}-{packet_name}.md` (the brief in `docs/reviews/brief.md` "
        f"followed by the eight branches in brief, the treatment records with the publications and promises logged against them, and the method extract).\n\n"
        f"Rulings: `docs/reviews/{today}-rulings.md`.\n\n---\n\n"
    )
    out.write_text(header + text.strip() + "\n")
    print(f"filed {out.relative_to(ROOT)}: model {version}, finish {finish}, {len(queries)} searches, "
          f"{usage.get('candidatesTokenCount', '?')} tokens out, {took:.0f} s; raw reply at {raw_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
