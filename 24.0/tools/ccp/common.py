import os, time
import json, base64, zipfile
import requests

cfg = {
    "context" : None,
    "auth_ep" : None,
    "ccp_request" : None,
    "ccp_ep" : None,
    "ccp_method_id" : None,
    "ogc_request" : None,
    "token" : None
}

def initAuth():
    cfg["refreshtoken"] = os.environ["OIDC_REFRESH_TOKEN"]
    tokarr = cfg["refreshtoken"].split(".")
    padded = tokarr[1] +"="*divmod(len(tokarr[1]),4)[1]
    jsontok = json.loads(base64.urlsafe_b64decode(padded))
    cfg["auth_ep"] = jsontok["iss"] + "/protocol/openid-connect/token"
    print(f"Auth ep is: {cfg["auth_ep"]}")

def getToken():
    tokresp = requests.post(cfg["auth_ep"],
        data={"grant_type" : "refresh_token", "client_id" : "galaxy-test", "refresh_token" : cfg["refreshtoken"]},
        headers={ "X-D4Science-Context" : cfg["context"]})
    if not tokresp.ok:
        raise Exception(f"You are not authorized for this operation {tokresp.status_code} - {tokresp.text}")
    jwt = tokresp.json()["access_token"]
    return jwt

def sendRequest():
    token = getToken()
    # Request method execution
    resp = requests.post(f"{cfg["ccp_ep"]}/processes/{cfg["ccp_method_id"]}/execution", json=cfg["request"], headers={"Authorization" : "Bearer " + token})
    if resp.status_code != 200:
        jobStatus = resp.json()
    else:
        raise Exception("Unable to start execution")
    return jobStatus

def poll(jobStatus):
    token = getToken()
    errcount = 0
    while jobStatus["status"] != "successful" and jobStatus["status"] != "failed":
        print(time.strftime("[%H:%m:%S] ") + jobStatus["status"] + ": " + jobStatus["message"])
        time.sleep(5)
        resp = requests.get(cfg["ccp_ep"] + "/jobs/" + jobStatus["jobID"], headers={"Authorization" : "Bearer " + token})
        if resp.ok:
            try:
                jobStatus = resp.json()
            except Exception as e:
                pass
        elif resp.status_code == 401:
            token = getToken()
        else:
            errcount += 1
            if errcount > 3:
                raise Exception(f"Error while polling: {resp.text}", resp.status_code)
            else:
                print(f"WARNING: Error while polling: {resp.text} ({resp.status_code})")
      
    print(time.strftime("[%H:%m:%S] ") + jobStatus["status"] + ": " + jobStatus["message"])
    resp = requests.get(cfg["ccp_ep"] + "/executions/" + jobStatus["jobID"], headers={"Accept" : "application/json", "Authorization" : "Bearer " + token})
    print(json.dumps(resp.json(), indent=2))
    return jobStatus

def showDir(path):
  for r, d, f in os.walk(path): print(f"root {r}, directories {d}, files {f}")

def buildOutput(jobStatus):
    token = getToken()
    if jobStatus["status"] == "successful":
        resp = requests.get(cfg["ccp_ep"] + "/executions/" + jobStatus["jobID"] + "/outputs/output.zip", headers={"Authorization" : "Bearer " + token})
        showDir(".")
        outputfile = "output.zip"
        if(resp.status_code == 200):
            open(outputfile, "wb").write(resp.content)
            with zipfile.ZipFile("output.zip","r") as zip_ref:
                zip_ref.extractall("")
            showDir(".")
        else:
            raise Exception("Failed to download output: " + resp.status_code)