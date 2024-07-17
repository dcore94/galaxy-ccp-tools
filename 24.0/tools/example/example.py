import sys
import os
import requests
token = os.environ["OIDC_ACCESS_TOKEN"]
resp = requests.get("https://ccp.cloud-dev.d4science.org/executions", headers={"Authorization" : "Bearer " + token})
outfile = open(sys.argv[1], "w")
outfile.write(resp.text)

resp = requests.get("https://ccp.cloud-dev.d4science.org/processes", headers={"Authorization" : "Bearer " + token})
outfile = open(sys.argv[2], "w")
outfile.write(resp.text)