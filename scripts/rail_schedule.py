#!/usr/bin/env python3
"""Israel Railways public timetable helper.

Uses the public railway.co.il/en HTML timetable form. This is not an official API.

Examples:
  python rail_schedule.py stations --filter Herzliya
  python rail_schedule.py route --from 3700 --to 1600 --time 10:50
  python rail_schedule.py route --from "Tel Aviv - Savidor" --to Nahariya --time now --after-now
  python rail_schedule.py rescue --from "Tel Aviv - Savidor" --intended Herzliya --towards Nahariya --time now
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict
from typing import Iterable
from zoneinfo import ZoneInfo

BASE_URL = "https://railway.co.il/en"
UA = "Mozilla/5.0 (Hermes Israel Railways schedule skill)"


@dataclass
class Stop:
    name: str
    time: str
    platform: str | None = None
    kind: str | None = None  # Departure / Arrival / None


@dataclass
class Train:
    train_no: str
    departure: str
    arrival: str
    route_text: str
    stops: list[Stop]


def fetch(url: str, params: dict[str, str] | None = None, timeout: int = 25) -> str:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")


def normalize_text(raw_html: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", raw_html))
    return re.sub(r"\s+", " ", text).strip()


def get_stations() -> list[tuple[str, str]]:
    page = fetch(BASE_URL)
    seen: dict[str, str] = {}
    for value, name in re.findall(r'<option value="(\d+)"[^>]*>\s*([^<]+?)\s*</option>', page):
        name = html.unescape(name).strip()
        if name and name != "Choose station":
            seen[value] = name
    return sorted(seen.items(), key=lambda x: x[1].lower())


def resolve_station(value: str) -> str:
    value = value.strip()
    if value.isdigit():
        return value
    stations = get_stations()
    needle = value.lower()
    matches = [(sid, name) for sid, name in stations if needle in name.lower()]
    if not matches:
        raise SystemExit(f"No station matching: {value!r}")
    exact = [(sid, name) for sid, name in matches if name.lower() == needle]
    if len(exact) == 1:
        return exact[0][0]
    if len(matches) == 1:
        return matches[0][0]
    msg = "Ambiguous station. Matches:\n" + "\n".join(f"  {sid}  {name}" for sid, name in matches[:20])
    raise SystemExit(msg)


def israel_time_hhmm() -> str:
    return dt.datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%H:%M")


def parse_route_stops(route_text: str) -> list[Stop]:
    pattern = re.compile(
        r"(.+?)\s+–\s+(?:(Departure|Arrival)\s+)?(\d\d:\d\d)(?:\s+\|\s+Platform\s+([^\s]+))?(?=\s+[^–]+\s+–\s+(?:(?:Departure|Arrival)\s+)?\d\d:\d\d|\s*$)"
    )
    stops: list[Stop] = []
    for name, kind, t, platform in pattern.findall(route_text):
        name = name.strip()
        name = re.sub(r"^(Route Details Train Number \d+\s+)", "", name).strip()
        if name:
            stops.append(Stop(name=name, time=t, platform=platform or None, kind=kind or None))
    return stops


def query_trains(from_station: str, to_station: str, time: str = "now", date_type: str = "today") -> list[Train]:
    if time == "now":
        time = israel_time_hhmm()
    params = {
        "from_station": resolve_station(from_station),
        "to_station": resolve_station(to_station),
        "date_type": date_type,
        "time": time,
    }
    raw = fetch(BASE_URL, params=params)
    text = normalize_text(raw)
    if "The search failed" in text:
        raise SystemExit("railway.co.il search failed; check station IDs/date_type/time")
    pattern = re.compile(
        r"Train Number: (\d+) (\d\d:\d\d) Departure.*?(\d\d:\d\d) Arrival.*?Route Details Train Number \1 (.*?)(?=Ticket Prices)",
        re.S,
    )
    trains: list[Train] = []
    seen = set()
    for train_no, dep, arr, route in pattern.findall(text):
        key = (train_no, dep, arr, route[:200])
        if key in seen:
            continue
        seen.add(key)
        trains.append(Train(train_no=train_no, departure=dep, arrival=arr, route_text=route.strip(), stops=parse_route_stops(route.strip())))
    return trains


def filter_after_time(trains: Iterable[Train], hhmm: str) -> list[Train]:
    return [t for t in trains if t.departure >= hhmm]


def print_train(t: Train, compact: bool = False) -> None:
    print(f"Train {t.train_no}: {t.departure} → {t.arrival}")
    if compact:
        names = " → ".join(f"{s.name} {s.time}" for s in t.stops)
        print(names)
        return
    for s in t.stops:
        bits = [f"- {s.name}: {s.time}"]
        if s.kind:
            bits.append(f"({s.kind})")
        if s.platform:
            bits.append(f"platform {s.platform}")
        print(" ".join(bits))


def cmd_stations(args: argparse.Namespace) -> None:
    stations = get_stations()
    if args.filter:
        needle = args.filter.lower()
        stations = [(sid, name) for sid, name in stations if needle in name.lower()]
    if args.json:
        print(json.dumps([{"id": sid, "name": name} for sid, name in stations], ensure_ascii=False, indent=2))
    else:
        for sid, name in stations:
            print(f"{sid}\t{name}")


def cmd_route(args: argparse.Namespace) -> None:
    query_time = israel_time_hhmm() if args.time == "now" else args.time
    trains = query_trains(args.from_station, args.to_station, args.time, args.date_type)
    if args.after_now:
        trains = filter_after_time(trains, query_time)
    if args.limit:
        trains = trains[: args.limit]
    if args.json:
        print(json.dumps([asdict(t) for t in trains], ensure_ascii=False, indent=2))
        return
    print(f"Query time: {query_time} Israel time")
    if not trains:
        print("No trains found.")
        return
    for i, t in enumerate(trains):
        if i:
            print()
        print_train(t, compact=args.compact)


def cmd_rescue(args: argparse.Namespace) -> None:
    query_time = israel_time_hhmm() if args.time == "now" else args.time
    trains = query_trains(args.from_station, args.towards, args.time, args.date_type)
    intended = args.intended.lower()
    candidates = [t for t in trains if not any(intended in s.name.lower() for s in t.stops)]

    scored: list[tuple[int, Train, int]] = []
    for t in candidates:
        idx = 1 if len(t.stops) > 1 else 0
        if args.passed:
            found = False
            for i, st in enumerate(t.stops[:-1]):
                if args.passed.lower() in st.name.lower():
                    if st.time <= query_time <= t.stops[i + 1].time:
                        score = 0
                    elif st.time <= query_time:
                        score = 1
                    else:
                        score = 2
                    scored.append((score, t, i + 1))
                    found = True
                    break
            if not found:
                continue
        else:
            score = 0 if t.departure >= query_time else 1
            scored.append((score, t, idx))

    if not scored:
        raise SystemExit("No matching train found. Provide --passed or a farther --towards station.")
    scored.sort(key=lambda x: (x[0], x[1].departure))
    _, t, idx = scored[0]
    next_stop = t.stops[idx]
    print(f"Matched train {t.train_no}.")
    print(f"Next stop: {next_stop.name} at {next_stop.time}" + (f", platform {next_stop.platform}" if next_stop.platform else ""))
    print("Route:")
    print_train(t, compact=True)

    if args.recovery:
        print("\nRecovery route:")
        recovery = query_trains(next_stop.name, args.intended, next_stop.time, args.date_type)
        recovery = filter_after_time(recovery, next_stop.time) or recovery
        if recovery:
            print_train(recovery[0], compact=True)
        else:
            print("No recovery train found.")


def main() -> None:
    ap = argparse.ArgumentParser(description="Israel Railways public timetable helper")
    sub = ap.add_subparsers(required=True)

    sp = sub.add_parser("stations", help="List or search station IDs")
    sp.add_argument("--filter", help="Substring filter, e.g. Herzliya")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_stations)

    rp = sub.add_parser("route", help="Query route schedule")
    rp.add_argument("--from", dest="from_station", required=True, help="Station ID or name substring")
    rp.add_argument("--to", dest="to_station", required=True, help="Station ID or name substring")
    rp.add_argument("--time", default="now", help="HH:MM or now")
    rp.add_argument("--date-type", default="today", choices=["today", "tomorrow"])
    rp.add_argument("--after-now", action="store_true", help="Only show departures >= query time")
    rp.add_argument("--limit", type=int, default=5)
    rp.add_argument("--compact", action="store_true")
    rp.add_argument("--json", action="store_true")
    rp.set_defaults(func=cmd_route)

    rs = sub.add_parser("rescue", help="Identify likely train that skipped intended station")
    rs.add_argument("--from", dest="from_station", required=True, help="Boarding station ID/name")
    rs.add_argument("--intended", required=True, help="Intended station ID/name, e.g. Herzliya")
    rs.add_argument("--towards", default="Nahariya", help="Far destination to query toward, default Nahariya")
    rs.add_argument("--passed", help="Last station known passed/stopped, e.g. Tel Aviv - University")
    rs.add_argument("--time", default="now", help="HH:MM or now")
    rs.add_argument("--date-type", default="today", choices=["today", "tomorrow"])
    rs.add_argument("--recovery", action="store_true", help="Also query route from next stop back to intended station")
    rs.set_defaults(func=cmd_rescue)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
