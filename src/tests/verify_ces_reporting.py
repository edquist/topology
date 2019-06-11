#!/usr/bin/python

import json
import requests


baseurl   = 'https://gracc.opensciencegrid.org/q'
indexurl  = baseurl  + '/gracc.osg.summary'
searchurl = indexurl + '/_search'
#counturl  = indexurl + '/_count'
#scrollurl = baseurl  + '/_search/scroll'

def bucket2fqdn(b):
    # extract fqdn from the ProbeName in a CE bucket from ES
    return b['key'].split(':')[1]

def get_gracc_reporting_CEs():
    # query gracc for unique ProbeName's reported in the last year

    ce_query = {
        "query": {
            "bool": {
                "must": [
                    { "term": { "ResourceType": "Batch" } },
                    { "range": { "EndTime": { "gte": "now-1y" } } }
                ]
            }
        },
        "size": 0,
        "aggs": {
            "CEs" : {
                "terms": {"field" : "ProbeName", "size" : 10000}
            }
        }
    }

    res = requests.get(searchurl, json=ce_query).json()

    buckets = res['aggregations']['CEs']['buckets']

    fqdns = set(map(bucket2fqdn, buckets))

    return fqdns


