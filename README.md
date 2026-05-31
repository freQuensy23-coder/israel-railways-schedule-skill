# Israel Railways Schedule Skill

A reusable Hermes Agent skill for checking Israel Railways schedules through the public `railway.co.il/en` timetable form.

It documents:

- common Israel Railways station IDs;
- how to extract the ID of any station from the public form;
- how to query the timetable form with `from_station`, `to_station`, `date_type`, and `time`;
- how to parse route details from returned HTML;
- how to identify a train's next stop when someone boarded the wrong train;
- how to find a recovery route back to the intended station.

## Install in Hermes

```bash
hermes skills install https://raw.githubusercontent.com/freQuensy23-coder/israel-railways-schedule-skill/main/SKILL.md
```

Or manually copy `SKILL.md` into:

```text
~/.hermes/skills/productivity/israel-railways-schedule/SKILL.md
```


## CLI helper script

This repo also includes a ready-to-run parser:

```bash
python scripts/rail_schedule.py stations --filter Herzliya
python scripts/rail_schedule.py route --from 3700 --to 1600 --time 10:50 --after-now --limit 1 --compact
python scripts/rail_schedule.py rescue --from 3700 --intended Herzliya --towards Nahariya --time 10:50 --passed "Tel Aviv - University" --recovery
```

The script uses only the Python standard library.

## Important note

This skill does **not** use an official Israel Railways API. It uses the public timetable page, which accepts GET parameters and returns HTML schedule results.

For live disruptions, cancellations, or platform changes, verify with the official Israel Railways app/site when possible.

## License

MIT
