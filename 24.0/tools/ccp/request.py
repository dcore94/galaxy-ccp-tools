import sys
from common import *

ccp_request = json.load(open(sys.argv[1]))
cfg["context"] = ccp_request["context"]
cfg["ccp_ep"] = ccp_request["ccp_ep"]
cfg["ccp_method_id"] = ccp_request["ccp_method_id"]
cfg["request"] = ccp_request["request"]
print(f"Context is: {cfg["context"]}. CCP EP is {cfg["ccp_ep"]}. Method id is {cfg["ccp_method_id"]}")

initAuth()
jobStatus = sendRequest()
jobStatus = poll(jobStatus)
buildOutput(jobStatus)