"""Lab Accession API built with Pixeltable.

    pxt schema update app.py lab
    pxt service run app.py lab
"""
from pixeltable.serving import FastAPIRouter

from models import Assignments, Samples, Stations, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import batch, station_queue

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
