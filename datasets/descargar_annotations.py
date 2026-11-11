from cryoet_data_portal import (
  Client,
  Run,
)

client = Client()
run = Run.get_by_id(client, 35016)

for annotation in run.annotations:
  annotation.download()