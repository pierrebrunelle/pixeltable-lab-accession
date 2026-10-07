"""Three related tables: stations, samples and assignments."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import priority_name, station_label, urgency_band

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
