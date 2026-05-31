---
name: israel-railways-schedule
description: Use when checking Israel Railways schedules from the public railway.co.il form, especially to identify a train's next stop, station IDs, route stops, platforms, and recovery routes after boarding the wrong train.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [israel, railways, transit, schedules, web-fetch]
    related_skills: [maps]
---

# Israel Railways Schedule via railway.co.il

## Overview

Use the public `railway.co.il/en` timetable page as a schedule source when the user needs fast, concrete Israel Railways information: next stop, route stops, train number, platform, or how to recover after missing a station.

This is **not an official API**. It is a public HTML form that accepts GET parameters and returns schedule results in the page HTML. Treat it as a pragmatic fetch/parsing workflow.

Core form URL:

```text
https://railway.co.il/en
```

Core GET parameters:

```text
from_station=<station_id>
to_station=<station_id>
date_type=today|tomorrow
time=HH:MM
```

Example:

```text
https://railway.co.il/en?from_station=3700&to_station=1600&date_type=today&time=10%3A50
```

This asks for trains from **Tel Aviv - Savidor Center** to **Nahariya** today around `10:50`.

## When to Use

Use this when:

- The user is on an Israel Railways train and needs the next stop now.
- The user missed Herzliya / Tel Aviv / airport / Haifa and needs a recovery route.
- You need station IDs for Israel Railways schedule queries.
- You need concrete route details: train number, intermediate stops, platforms, departure/arrival times.

Do **not** use this as proof of official real-time disruption status. For cancellations, strikes, security disruptions, or live platform changes, prefer the official Israel Railways app/site if accessible and warn that the public HTML may lag.

## Station IDs: Common Stations

These IDs are taken from the `railway.co.il/en` form `<option value="...">Station Name</option>`.

### Tel Aviv / Center

- `4900` — Tel Aviv - HaHagana
- `4600` — Tel Aviv - HaShalom
- `3700` — Tel Aviv - Savidor Center
- `3600` — Tel Aviv - University - Expo
- `3500` — Herzliya
- `3400` — Bet Yehoshua
- `3300` — Netanya
- `3310` — Netanya - Sapir
- `3100` — Hadera - West
- `2800` — Binyamina

### North / Coast

- `2820` — Caesarea - Pardes Hanna
- `2500` — Atlit
- `2300` — Haifa - Hof HaCarmel
- `2200` — Haifa - Bat Gallim
- `2100` — Haifa - Merkaz HaShmona
- `1220` — HaMifrats Central Station
- `1300` — Hutsot HaMifrats
- `700` — Kiryat Hayim
- `1400` — Kiryat Motzkin
- `1500` — Akko
- `1600` — Nahariya
- `1820` — Ahihud
- `1840` — Karmi'el
- `1260` — Afula
- `1280` — Bet She'an – David Levy
- `1250` — Migdal Ha'Emek - Kfar Barukh
- `1240` — Yokne'am - Kfar Yehoshua

### Airport / Jerusalem

- `8600` — Ben Gurion Airport
- `680` — Jerusalem - Yitzhak Navon
- `6500` — Jerusalem - Biblical Zoo
- `6700` — Jerusalem - Malha
- `6300` — Bet Shemesh

### South / Shephelah / Beer Sheva

- `5800` — Ashdod - Ad Halom
- `5900` — Ashkelon
- `7300` — Be'er Sheva - North - University
- `7320` — Be'er Sheva - Center
- `7500` — Dimona
- `9650` — Netivot
- `9700` — Ofakim
- `9600` — Sderot
- `7000` — Kiryat Gat
- `8550` — Lehavim - Rahat
- `6150` — Kiryat Mal'akhi - Yo'av
- `6900` — Mazkeret Batya
- `5000` — Lod
- `5150` — Lod - Ganne Aviv
- `5010` — Ramla
- `5200` — Rehovot
- `5300` — Be'er Ya'akov
- `5410` — Yavne - East
- `9000` — Yavne - West

### Gush Dan / Sharon / Petah Tikva / Rishon / Modi'in

- `4100` — Bne Brak
- `4250` — Petah Tikva - Sgulla
- `4170` — Petah Tikva - Kiryat Arye
- `9200` — Hod HaSharon - Sokolov
- `8700` — Kfar Sava - Nordau
- `2960` — Ra'anana - South
- `2940` — Ra'anana - West
- `8800` — Rosh HaAyin - North
- `9100` — Rishon LeTsiyon - HaRishonim
- `9800` — Rishon LeTsiyon - Moshe Dayan
- `4640` — Holon Junction
- `4660` — Holon - Wolfson
- `4680` — Bat Yam – Eli Cohen – Yoseftal
- `4690` — Bat Yam - HaKomemiyut
- `400` — Modi'in Center
- `300` — Pa'ate Modi'in
- `4800` — Kfar Chabad

**Important:** For anything critical, do not rely only on the remembered table. Re-extract station IDs from the live form before answering.

## How to Get the ID of Any Station

Fetch the form page and parse the `<option>` elements.

Use shell/Python if native `web_extract` is not enough because `web_extract` summarizes and may omit form options.

```bash
python3 - <<'PY'
import requests, re, html
page = requests.get('https://railway.co.il/en', headers={'user-agent':'Mozilla/5.0'}, timeout=20).text
for value, name in re.findall(r'<option value="(\d+)"[^>]*>\s*([^<]+?)\s*</option>', page):
    name = html.unescape(name).strip()
    if name and name != 'Choose station':
        print(value, name)
PY
```

To find a specific station:

```bash
python3 - <<'PY'
import requests, re, html
needle = 'Herzliya'.lower()
page = requests.get('https://railway.co.il/en', headers={'user-agent':'Mozilla/5.0'}, timeout=20).text
for value, name in re.findall(r'<option value="(\d+)"[^>]*>\s*([^<]+?)\s*</option>', page):
    name = html.unescape(name).strip()
    if needle in name.lower():
        print(value, name)
PY
```

## Ready-to-Use Script

This skill includes a working parser script:

```bash
~/.hermes/skills/productivity/israel-railways-schedule/scripts/rail_schedule.py
```

Use it before rewriting ad hoc parsing code.

Examples:

```bash
# Find station IDs
rail_schedule.py stations --filter Herzliya

# Query a route by station IDs or name substrings
rail_schedule.py route --from 3700 --to 1600 --time 10:50 --after-now --limit 1 --compact
rail_schedule.py route --from "Tel Aviv - Savidor" --to Nahariya --time now --limit 3

# Live rescue: boarded in Tel Aviv, intended Herzliya, train skipped it
rail_schedule.py rescue --from 3700 --intended Herzliya --towards Nahariya --time 10:50 --passed "Tel Aviv - University" --recovery
```

The `rescue` command matches trains that do not include the intended station and, when `--passed` is supplied, prefers the train where the passed station time is before the query time and the next stop is after it.

## How to Query the Schedule Form

Use a GET request to `https://railway.co.il/en` with these fields:

- `from_station`: numeric station ID
- `to_station`: numeric station ID
- `date_type`: usually `today` or `tomorrow`
- `time`: local Israel time in `HH:MM`

Example: Tel Aviv Savidor → Nahariya today at 10:50:

```bash
python3 - <<'PY'
import requests
params = {
    'from_station': '3700',
    'to_station': '1600',
    'date_type': 'today',
    'time': '10:50',
}
r = requests.get('https://railway.co.il/en', params=params, headers={'user-agent':'Mozilla/5.0'}, timeout=20)
print(r.url)
print(r.status_code, len(r.text))
open('/tmp/rail.html', 'w').write(r.text)
PY
```

The returned HTML includes result blocks containing text like:

```text
Train Number: 160
10:28 Departure Platform 1
12:13 Arrival Platform 1
Route Details Train Number 160
Tel Aviv - Savidor Center – Departure 10:28 | Platform 1
Tel Aviv - University - Expo – 10:31 | Platform 1
Binyamina – 11:01 | Platform 2
Atlit – 11:14 | Platform 2
...
```

## Extracting Train Routes from Returned HTML

The page is HTML, but the route text is easy to parse after stripping tags.

```bash
python3 - <<'PY'
import requests, re, html

params = {
    'from_station': '3700',      # Tel Aviv - Savidor Center
    'to_station': '1600',        # Nahariya
    'date_type': 'today',
    'time': '10:50',
}
raw = requests.get('https://railway.co.il/en', params=params, headers={'user-agent':'Mozilla/5.0'}, timeout=20).text
text = html.unescape(re.sub('<[^>]+>', ' ', raw))
text = re.sub(r'\s+', ' ', text)

pattern = r'Train Number: (\d+) (\d\d:\d\d) Departure.*?(\d\d:\d\d) Arrival.*?Route Details Train Number \1 (.*?)(?=Ticket Prices)'
for train_no, dep, arr, route in re.findall(pattern, text):
    print('\nTRAIN', train_no, 'dep', dep, 'arr', arr)
    print(route[:1000])
PY
```

## Identifying the User's Current Train

When the user says “I boarded from Tel Aviv, expected Herzliya, but the train skipped it,” do this:

1. Get current Israel time:

```bash
TZ=Asia/Jerusalem date '+%Y-%m-%d %H:%M:%S %Z'
```

2. Query northbound long routes from likely Tel Aviv origin stations to a far northern destination, usually `Nahariya` (`1600`) or `Haifa - Hof HaCarmel` (`2300`).

Use likely Tel Aviv origins:

- `4900` — Tel Aviv HaHagana
- `4600` — Tel Aviv HaShalom
- `3700` — Tel Aviv Savidor Center
- `3600` — Tel Aviv University - Expo

3. Find trains whose route:

- has a Tel Aviv stop near the current time;
- goes north;
- does **not** include `Herzliya`;
- has the next stop after the last passed Tel Aviv station.

4. Answer with the exact next stop and time, plus recovery route.

Example observed pattern:

```text
Train 160:
Tel Aviv HaShalom — 10:21
Tel Aviv Savidor — 10:28
Tel Aviv University — 10:31
Binyamina — 11:01
Atlit — 11:14
Haifa Hof HaCarmel — 11:24
```

If the user passed Herzliya without stopping on that train, the next stop is **Binyamina**.

## Finding a Recovery Route

If the user needs to get back to a missed station, query from the next stop back to the intended station.

Example: Binyamina → Herzliya after arriving at Binyamina around 11:01:

```bash
python3 - <<'PY'
import requests, re, html
params = {
    'from_station': '2800',      # Binyamina
    'to_station': '3500',        # Herzliya
    'date_type': 'today',
    'time': '11:01',
}
raw = requests.get('https://railway.co.il/en', params=params, headers={'user-agent':'Mozilla/5.0'}, timeout=20).text
text = html.unescape(re.sub('<[^>]+>', ' ', raw))
text = re.sub(r'\s+', ' ', text)
pattern = r'Train Number: (\d+) (\d\d:\d\d) Departure.*?(\d\d:\d\d) Arrival.*?Route Details Train Number \1 (.*?)(?=Ticket Prices)'
for train_no, dep, arr, route in re.findall(pattern, text):
    if dep >= '11:01':
        print('TRAIN', train_no, 'dep', dep, 'arr', arr)
        print(route[:800])
        break
PY
```

Example result:

```text
Train 243
Binyamina — 11:07
Hadera - West — 11:17
Netanya — 11:27
Netanya - Sapir — 11:32
Bet Yehoshua — 11:35
Herzliya — 11:43
```

## Answer Style for Live Transit Rescue

When the user is physically on a train, answer first with the action:

```text
Выходи на Binyamina в 11:01. Это следующая остановка.
Обратный поезд до Herzliya: Binyamina 11:07 → Herzliya 11:43, train 243.
```

Then give the evidence route only if useful:

```text
Я сопоставил поезд по расписанию: Tel Aviv Savidor 10:28 → University 10:31 → Binyamina 11:01, без Herzliya/Netanya в маршруте.
```

Do not say “скорее всего” once the route has been matched. If the match is uncertain, say exactly what is missing: “нужна станция посадки или текущее время/номер поезда”.

## Common Pitfalls

1. **Confusing search with fetch.** Web search is not enough. Use the form HTML or direct GET request.

2. **Calling it an official API.** It is a public form endpoint returning HTML, not a documented official API.

3. **Using `date=YYYY-MM-DD`.** The page form uses `date_type=today|tomorrow`; `date=...` can return “search failed”.

4. **Trusting station IDs from memory for critical answers.** Re-extract from the live form if the answer affects a live trip.

5. **Assuming every northbound train stops at Netanya.** Some express trains from Tel Aviv skip Herzliya/Netanya/Beit Yehoshua and next stop at Binyamina.

6. **Overexplaining during rescue.** Give the immediate action first, then details.

7. **Using Wikipedia station layout for transfers.** If Wikipedia has a station-layout description (`Platforms`, `Tracks`, `side platform`, `island platform`, numbering direction), use it to answer whether two platform numbers are the same physical island or require a tunnel/bridge. Example: Binyamina is `1 side platform + 1 island platform`, with tracks 1–3 east→west, so 2↔3 is the same island and 1↔2/3 requires the pedestrian tunnel/bridge; if Wikipedia lacks this layout data, say the physical transfer is not verified.

## Verification Checklist

- [ ] Current Israel time checked with `TZ=Asia/Jerusalem date`.
- [ ] Station IDs verified from live `railway.co.il/en` form if critical.
- [ ] Schedule queried with `from_station`, `to_station`, `date_type`, `time`.
- [ ] Route details parsed from returned HTML, not inferred from search snippets.
- [ ] Next stop/time identified from the matched train route.
- [ ] Recovery route queried separately if the user needs to get back.
