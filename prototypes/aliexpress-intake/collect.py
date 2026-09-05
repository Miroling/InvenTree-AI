"""Throwaway public-source collector for the fixed example; no inventory API."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser

SOURCES = {
    "seller.html": "https://www.aliexpress.com/item/1005009814305006.html",
    "manufacturer.html": "https://www.hynetek.com/2421.html",
    "manufacturer-full.pdf": "https://www.hynetek.com/uploadfiles/site/219/news/c16af076-8c40-4e8d-b126-b4f9b83e86ea.pdf",
}
class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("property") in ("og:title", "og:type"):
            self.values[attrs["property"]] = attrs.get("content", "")

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obscura", default="obscura")
    args = parser.parse_args()
    output = Path(__file__).parent / ".prototype-cache"
    output.mkdir(mode=0o700, exist_ok=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith("OBSCURA_")}
    env["OBSCURA_PROFILE"] = "2"
    records = []
    for filename, url in SOURCES.items():
        record = {"source_url": url, "retrieved_at": datetime.now(timezone.utc).isoformat()}
        try:
            result = subprocess.run([args.obscura, "fetch", url, "--stealth", "--dump", "original", "--timeout", "30", "--quiet"], env=env, capture_output=True, timeout=45)
            if result.returncode:
                record["status"] = "fetch_failed"
                record["exit_code"] = result.returncode
            else:
                raw = result.stdout
                (output / filename).write_bytes(raw)
                record.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
                if filename.endswith(".pdf"):
                    record["status"] = "pdf_signature_present" if raw.startswith(b"%PDF-") else "invalid_pdf"
                    record["review_required"] = "Parse the PDF, verify revision, exact variant and cited pages. A signature alone does not verify specifications."
                else:
                    metadata = Metadata()
                    metadata.feed(raw.decode("utf-8", errors="replace"))
                    record.update(status="html_received_unverified", metadata=metadata.values)
        except (OSError, subprocess.TimeoutExpired) as error:
            record.update(status="collection_failed", error_type=type(error).__name__)
        records.append(record)
        print(filename, record["status"])
    (output / "manifest.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    print("Review manifest:", output / "manifest.json")

if __name__ == "__main__":
    main()
