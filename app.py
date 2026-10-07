"""Lab Accession API built with Pixeltable.

    pxt schema update app.py lab
    pxt service run app.py lab
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import priority_name, station_label, urgency_band

# ---- tables ----
TableModel = pxt.model_base()


class Stations(TableModel, name='stations'):
    station_id = pxt.Column(type=pxt.String, primary_key=True)
    name: pxt.String
    capacity: pxt.Int

    label = station_label(name, capacity)


class Samples(TableModel, name='samples'):
    accession_id = pxt.Column(type=pxt.String, primary_key=True)
    specimen: pxt.String
    priority: pxt.Int
    received_at: pxt.String
    batch_code: pxt.String | None

    priority_label = priority_name(priority)


class Assignments(TableModel, name='assignments', has_default_idxs=False):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    accession_id: pxt.String
    station_id: pxt.String
    priority: pxt.Int
    delayed_min: pxt.Int
    status: pxt.String
    claimed_by: pxt.String | None

    urgency = urgency_band(priority, delayed_min)

    __indexes__ = [pxt.BtreeIndex(station_id), pxt.BtreeIndex(status)]


# ---- queries ----
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


# ---- routes ----
lab_api = FastAPIRouter(name='lab_api')
lab_api.add_insert_route(Stations, path='/stations', inputs=[Stations.station_id, Stations.name, Stations.capacity],
                         outputs=[Stations.station_id, Stations.label])
lab_api.add_insert_route(Samples, path='/samples',
                         inputs=[Samples.accession_id, Samples.specimen, Samples.priority, Samples.received_at,
                                 Samples.batch_code],
                         outputs=[Samples.accession_id, Samples.priority_label])
lab_api.add_insert_route(Assignments, path='/assignments',
                         inputs=[Assignments.accession_id, Assignments.station_id, Assignments.priority,
                                 Assignments.delayed_min, Assignments.status, Assignments.claimed_by],
                         outputs=[Assignments.id, Assignments.urgency])
lab_api.add_update_route(Assignments, path='/assignments/claim', inputs=[Assignments.status, Assignments.claimed_by],
                         outputs=[Assignments.id, Assignments.status, Assignments.claimed_by])
lab_api.add_compute_route(Assignments, path='/urgency', inputs=[Assignments.priority, Assignments.delayed_min],
                          outputs=[Assignments.urgency])
lab_api.add_query_route(path='/stations/queue', query=station_queue, method='get')
lab_api.add_query_route(path='/batches', query=batch, method='get')
