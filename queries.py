"""Queries across the accession tables."""
import pixeltable as pxt

from models import Assignments, Samples


@pxt.query
def station_queue(station_id: str):
    """Work for one station, most urgent first."""
    return Assignments.where(Assignments.station_id == station_id).select(
        Assignments.id, Assignments.accession_id, Assignments.urgency, Assignments.status, Assignments.claimed_by
    ).order_by(Assignments.priority, asc=False)


@pxt.query
def batch(batch_code: str):
    """Samples received in one batch."""
    return Samples.where(Samples.batch_code == batch_code).select(
        Samples.accession_id, Samples.specimen, Samples.priority_label
    ).order_by(Samples.accession_id)
