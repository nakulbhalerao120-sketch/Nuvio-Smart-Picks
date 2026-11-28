"""Select one pending official TV beta, oldest first, so a missed run is recoverable."""
import json
import os
import re
import subprocess
from pathlib import Path

base = "1.2.0-beta.4"
owner = "NuvioMedia/NuvioTV"
destination = os.environ["GITHUB_REPOSITORY"]
def releases(repo):
    raw = subprocess.check_output(["gh", "api", "--paginate", "--slurp", f"repos/{repo}/releases?per_page=100"])
    return [release for page in json.loads(raw) for release in page if not release["draft"]]

pattern = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)-beta\.(\d+)$")
def number(tag):
    match = pattern.fullmatch(tag)
    return tuple(map(int, match.groups())) if match else ()

existing = releases(destination)
versions = {}
for release in existing:
    match = re.fullmatch(r"tv-v(.+)-?\.tv\.(\d+)", release["tag_name"])
    if match and any(asset["name"] == "Nuvio-v2-TV-armeabi-v7a.apk" for asset in release["assets"]):
        versions[number(match[1])] = max(versions.get(number(match[1]), 0), int(match[2]))
pending = sorted((number(r["tag_name"]), r["tag_name"]) for r in releases(owner)
                 if number(r["tag_name"]) >= number(base) and (number(r["tag_name"]) not in versions or (number(r["tag_name"]) == number(base) and versions[number(base)] < 1087))
                 and any(a["name"].lower().endswith(".apk") for a in r["assets"]))
if pending:
    _, tag = pending[0]
    code = max([1085, *versions.values()]) + 1
    with Path(os.environ["GITHUB_OUTPUT"]).open("a") as out:
        print(f"tag={tag}\ncode={code}\nversion={tag.removeprefix('v')}.tv.{code}",file=out)
