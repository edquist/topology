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

def runcmd(cmdline):
    from subprocess import Popen, PIPE
    p = Popen(cmdline, stdout=PIPE)
    out, err = p.communicate()
    return p.returncode, out

def print_errors(errors):
    if errors:
        print("Commit is not eligible for auto-merge:")
        for e in errors:
            print(e)
    else:
        print("Commit is eligible for auto-merge.")

if __name__ == '__main__':
    main(sys.argv[1:])

