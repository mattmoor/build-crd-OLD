"""A build controller."""


import httplib2
from oauth2client.contrib.gce import AppAssertionCredentials
from apiclient.discovery import build as discovery_build

import hashlib
import json
from kubernetes import client, config, watch
import logging
import os
import time

DOMAIN = "mattmoor.io"

def main():
    config.load_incluster_config()

    crds = client.CustomObjectsApi()

    creds = AppAssertionCredentials()
    cloudbuild = discovery_build('cloudbuild', 'v1', credentials=creds)

    def watch_until_done(obj, operation):
        name = operation["name"]
        while not operation.get("done", False):
            logging.error("Waiting on: %s", name)
            time.sleep(1)
            operation = cloudbuild.operations().get(name=name).execute()

        logging.error("Complete: %s", name)
        spec = obj["spec"]
        spec["Status"] = "DONE"
        if "error" in operation:
            spec["error"] = operation["error"]
        else:
            spec["response"] = operation["response"]
        crds.replace_namespaced_custom_object(DOMAIN, "v1", obj["metadata"]["namespace"],
                                              "builds", obj["metadata"]["name"], obj)

    def build(obj):
        spec = obj["spec"]
        if "Operation" in spec:
            return
        operation = cloudbuild.projects().builds().create(projectId='convoy-adapter', body=spec).execute()
        spec["Operation"] = operation["name"]
        obj = crds.replace_namespaced_custom_object(DOMAIN, "v1", obj["metadata"]["namespace"],
                                              "builds", obj["metadata"]["name"], obj)
        logging.error("Waiting until %s is done", operation["name"])
        watch_until_done(obj, operation)

    # TODO(mattmoor): On startup we should start a thread to watch any in-progress builds.

    stream = watch.Watch().stream(crds.list_cluster_custom_object, DOMAIN, "v1", "builds")
    for event in stream:
        # TODO(mattmoor): Execute in a threadpool.
        try:
            build(event["object"])
        except:
            logging.exception("Error handling event")

if __name__ == "__main__":
    main()
