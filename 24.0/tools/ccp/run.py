
from common import *

print(open("request.json").read())
cfg["request"] = json.load(open("request.json"))
cfg["context"] = os.environ["context"]
cfg["ccp_ep"] = os.environ["ccp_ep"]
cfg["ccp_method_id"] = os.environ["ccp_method_id"]
print(f"Context is: {cfg["context"]}. CCP EP is {cfg["ccp_ep"]}. Method id is {cfg["ccp_method_id"]}")

initAuth()

jobStatus = sendRequest()
jobStatus = poll(jobStatus)
buildOutput(jobStatus)