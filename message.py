import clx.xms
import requests

client = clx.xms.Client(service_plan_id='434b917af66c4b5199b0fd7641281363', token='4c86ec6657c8483bb279e60d6f206dc1')

create = clx.xms.api.MtBatchTextSmsCreate()
create.sender = '447537404817'
create.recipients = {'918800602108'}
create.body = 'Hey this is ankit sending message using sinch'

try:
  batch = client.create_batch(create)
except (requests.exceptions.RequestException,
  clx.xms.exceptions.ApiException) as ex:
  print('Failed to communicate with XMS: %s' % str(ex))

