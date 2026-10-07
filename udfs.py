"""Pixeltable UDFs for the lab accession queue (recorded by module path, e.g. `udfs.urgency_band`)."""
import pixeltable as pxt


@pxt.udf
def priority_name(priority: int) -> str:
    return {1: 'routine', 2: 'urgent', 3: 'stat'}.get(priority, 'routine')


@pxt.udf
def urgency_band(priority: int, delayed_min: int) -> str:
    """Combine clinical priority and queueing delay into a triage band."""
    score = priority * 30 + min(delayed_min, 120)
    return 'red' if score >= 120 else ('amber' if score >= 70 else 'green')


@pxt.udf
def station_label(name: str, capacity: int) -> str:
    return f'{name} ({capacity}/h)'
