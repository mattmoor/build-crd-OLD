"""A build controller."""


import httplib2
from oauth2client.contrib.gce import AppAssertionCredentials
from apiclient.discovery import build as discovery_build

import hashlib
import json
from kubernetes import client, config, watch
import logging
import os

import inspect

DOMAIN = "mattmoor.io"

def main():
    config.load_incluster_config()

    crds = client.CustomObjectsApi()

    creds = AppAssertionCredentials()
    cloudbuild = discovery_build('cloudbuild', 'v1', credentials=creds)

    def build(obj):
        logging.error("List builds: %s", cloudbuild.projects().builds().list(projectId='convoy-adapter').execute())

    stream = watch.Watch().stream(crds.list_cluster_custom_object, DOMAIN, "v1", "builds")
    for event in stream:
        obj = event["object"]
        build(obj)

if __name__ == "__main__":
    main()
