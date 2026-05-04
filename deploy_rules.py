"""
Deploy Firestore security rules for samsel-app-92b36 using Google OAuth2 device flow.
Run: python deploy_rules.py
"""
import json, time, sys
import requests

PROJECT_ID = "samsel-app-92b36"
RULES_FILE = "firestore.rules"

# Firebase CLI's public OAuth2 client (open-source, safe to use)
CLIENT_ID     = "563584335869-fgrhgmd47bqnekij5i8b5pr03ho849e6.apps.googleusercontent.com"
CLIENT_SECRET = "j9iVZfS8yvn_CXWTMYPO3Rw"
SCOPE         = "https://www.googleapis.com/auth/cloud-platform"

def get_device_code():
    r = requests.post(
        "https://oauth2.googleapis.com/device/code",
        data={"client_id": CLIENT_ID, "scope": SCOPE}
    )
    r.raise_for_status()
    return r.json()

def poll_for_token(device_code, interval):
    while True:
        time.sleep(interval)
        r = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "device_code": device_code,
                "grant_type": "urn:ietf:params:oauth2:grant-type:device_code"
            }
        )
        data = r.json()
        if "access_token" in data:
            return data["access_token"]
        if data.get("error") == "authorization_pending":
            continue
        if data.get("error") == "slow_down":
            interval += 5
            continue
        print(f"Auth error: {data.get('error_description', data)}")
        sys.exit(1)

def create_ruleset(token, rules_source):
    r = requests.post(
        f"https://firebaserules.googleapis.com/v1/projects/{PROJECT_ID}/rulesets",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source": {
                "files": [{
                    "name": "firestore.rules",
                    "content": rules_source,
                    "fingerprint": ""
                }]
            }
        }
    )
    if not r.ok:
        print(f"Create ruleset failed: {r.status_code} {r.text}")
        sys.exit(1)
    return r.json()["name"]  # projects/.../rulesets/ID

def deploy_release(token, ruleset_name):
    release_name = f"projects/{PROJECT_ID}/releases/cloud.firestore"
    r = requests.patch(
        f"https://firebaserules.googleapis.com/v1/{release_name}",
        headers={"Authorization": f"Bearer {token}"},
        json={"release": {"name": release_name, "rulesetName": ruleset_name}}
    )
    if not r.ok:
        print(f"Deploy release failed: {r.status_code} {r.text}")
        sys.exit(1)
    print(f"[OK] Rules deployed: {r.json().get('rulesetName','')}")

# ── main ──────────────────────────────────────────────────────────────
with open(RULES_FILE) as f:
    rules_source = f.read()

print("=== SAMSEL Firestore Rules Deployer ===\n")
device = get_device_code()

print(f"1. Open this URL in your browser:\n\n   {device['verification_url']}\n")
print(f"2. Enter this code when prompted:\n\n   {device['user_code']}\n")
print("Waiting for you to authorise...")

token = poll_for_token(device["device_code"], device.get("interval", 5))
print("[OK] Authenticated\n")

print("Creating ruleset...")
ruleset_name = create_ruleset(token, rules_source)
print(f"[OK] Ruleset: {ruleset_name}\n")

print("Deploying release...")
deploy_release(token, ruleset_name)

print("\nDone! Firestore security rules are now live.")
