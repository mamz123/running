import os, json, requests

r = requests.post("https://www.strava.com/oauth/token", data={
    "client_id": os.environ["STRAVA_CLIENT_ID"],
    "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
    "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
    "grant_type": "refresh_token"})
r.raise_for_status()
token = r.json()["access_token"]

runs, page = [], 1
while True:
    res = requests.get("https://www.strava.com/api/v3/athlete/activities",
        headers={"Authorization": f"Bearer {token}"},
        params={"per_page": 200, "page": page})
    res.raise_for_status()
    batch = res.json()
    if not batch:
        break
    for a in batch:
        if a["sport_type"] in ("Run", "TrailRun", "VirtualRun"):
            runs.append({
                "name": a["name"],
                "date": a["start_date_local"],
                "distance_km": round(a["distance"] / 1000, 2),
                "moving_time_s": a["moving_time"],
                "elev_m": a["total_elevation_gain"],
                "avg_hr": a.get("average_heartrate"),
                "polyline": a["map"]["summary_polyline"],
            })
    page += 1

os.makedirs("site", exist_ok=True)
json.dump(runs, open("site/runs.json", "w"), indent=1)
print(f"Saved {len(runs)} runs")
