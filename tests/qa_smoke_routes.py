"""QA smoke test: log in as a real founder and hit every GET route.

Uses the predefined founder credentials against the real development database.
Only read-only GET requests are made; no data is modified.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app("development")

IDENTIFIER = "ceo@tavryc.com"
PASSWORD = "hassaan"

with app.app_context():
    from app.models.user import User

    user = User.query.filter(User.email == IDENTIFIER).first()
    if user is None:
        raise SystemExit(f"no user found for {IDENTIFIER} — run set_founder_passwords.py first")

client = app.test_client()

# 1) login — grab CSRF token from the login page first
login_page = client.get("/login")
m = re.search(rb'name="csrf_token"[^>]*value="([^"]+)"', login_page.data)
if not m:
    raise SystemExit("could not find csrf_token on login page")
token = m.group(1).decode()
resp = client.post(
    "/login", data={"identifier": IDENTIFIER, "password": PASSWORD, "csrf_token": token},
    follow_redirects=True,
)
print("LOGIN status:", resp.status_code)

# 2) hit every GET route
ok, skip, fail = [], [], []
for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
    methods = rule.methods - {"HEAD", "OPTIONS"}
    if methods != {"GET"}:
        continue
    endpoint = rule.endpoint
    if endpoint.startswith("static") or "debugtoolbar" in endpoint:
        continue
    # substitute simple converters
    path = str(rule)
    if "<" in path:
        skip.append((path, "has parameters"))
        continue
    resp = client.get(path)
    if resp.status_code == 200:
        ok.append(path)
    elif resp.status_code in (302, 308):
        skip.append((path, f"redirect {resp.status_code} -> {resp.headers.get('Location')}"))
    elif resp.status_code == 404:
        skip.append((path, "404"))
    else:
        fail.append((path, resp.status_code))

print(f"OK: {len(ok)}   REDIRECT/404: {len(skip)}   FAIL: {len(fail)}")
for p, r in fail:
    print("FAIL:", p, "->", r)
for p, r in skip:
    print("SKIP:", p, "->", r)
