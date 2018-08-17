#!/usr/bin/env python

import subprocess
import sys
import os
import re

def usage():
    print("Usage: %s BASE_SHA MERGE_COMMIT_SHA" % os.path.basename(__file__))
    sys.exit(1)

def main(args):
    insist(len(args) == 2)
    insist(looks_like_sha(args[0]))
    insist(looks_like_sha(args[1]))
    BASE_SHA, MERGE_COMMIT_SHA = args
    modified = get_modified_files(BASE_SHA, MERGE_COMMIT_SHA)
    errors = []
    DTs = []
    for fname in modified:
        if looks_like_downtime(fname):
            DTs += [fname]
        else:
            errors += ["File '%s' is not a downtime file." % fname]

    for fname in DTs:
        dtdict_base = get_downtime_dict_at_version(BASE_SHA, fname)
        dtdict_new  = get_downtime_dict_at_version(MERGE_COMMIT_SHA, fname)
        dtminus, dtplus = diff_dtdict(dtdict_base, dtdict_new)
        for dt in dtminus:
            print("Old Downtime %d modified: %s" % (dt["ID"], dt))
        for dt in dtminus:
            print("New Downtime %d modified: %s" % (dt["ID"], dt))

    print_errors(errors)
    sys.exit(len(errors) > 0)

def insist(cond):
    if not cond:
        usage()

def looks_like_sha(arg):
    return re.search(r'^[0-9a-f]{40}$', arg)  # is not None

def looks_like_downtime(fname):
    return re.search(r'^topology/[^/]+/[^/]+/[^/]+_downtime.yaml$', fname)

def get_modified_files(sha_a, sha_b):
    args = ['git', 'diff', '-z', '--name-only', sha_a, sha_b]
    ret, out = runcmd(args)
    if ret:
        sys.exit(1)
    return ret.rstrip('\0').split('\0')

def runcmd(cmdline, stderr=None):
    from subprocess import Popen, PIPE
    p = Popen(cmdline, stdout=PIPE, stderr=stderr)
    out, err = p.communicate()
    return p.returncode, out

def print_errors(errors):
    if errors:
        print("Commit is not eligible for auto-merge:")
        for e in errors:
            print(e)
    else:
        print("Commit is eligible for auto-merge.")

def get_file_at_version(sha, fname):
    args = ['git', 'show', '%s:%s' % (sha, fname)]
    ret, out = runcmd(args, open("/dev/null", "w"))
    return out

def get_downtime_dict_at_version(sha, fname):
    txt = get_file_at_version(sha, fname)
    dtlist = yaml.safe_load(txt) if txt else []
    return dict( (dt["ID"], dt) for dt in dtlist )

def diff_dtdict(dtdict_a, dtdict_b):
    def dt_changed(ID):
        return dtdict_a[ID] != dtdict_b[ID]
    dtids_a = set(dtdict_a)
    dtids_b = set(dtdict_b)
    dtids_mod = filter(dt_changed, dtids_a & dtids_b)
    dt_a = [ dtdict_a[ID] for ID in (dtids_a - dtids_b) | dtids_mod ]
    dt_b = [ dtdict_b[ID] for ID in (dtids_b - dtids_a) | dtids_mod ]

    return dt_a, dt_b

if __name__ == '__main__':
    main(sys.argv[1:])

