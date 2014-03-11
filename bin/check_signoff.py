#!/usr/bin/env python

# Checks that all commits have been signed off and fails if not.
# (Adapted from l33t Docker script for checking for their DCO)

import re
import os
import sys
import yaml
import subprocess

if 'TRAVIS' not in os.environ:
    print('TRAVIS is not defined; this should run in TRAVIS. Sorry.')
    sys.exit(127)

if os.environ['TRAVIS_PULL_REQUEST'] != 'false':
    commit_range = ['upstream/' + os.environ['TRAVIS_BRANCH'], 'FETCH_HEAD']
else:
    try:
        subprocess.check_call([
            'git', 'log', '-1', '--format=format:',
            os.environ['TRAVIS_COMMIT_RANGE'], '--',
        ])

        commit_range = os.environ['TRAVIS_COMMIT_RANGE'].split('...')

        # if it didn't split, it must have been separated by '..' instead
        if len(commit_range) == 1:
            commit_range = commit_range[0].split('..')

    except subprocess.CalledProcessError:
        print('TRAVIS_COMMIT_RANGE is invalid. This seems to be a force '
              'push. We will just assume it must be against upstream '
              'master and compare all commits in between.')

        commit_range = ['upstream/master', 'HEAD']

commit_format = '-%n hash: "%h"%n author: %aN <%aE>%n message: |%n%w(0,2,2).%B'

gitlog = subprocess.check_output([
    'git', 'log', '--reverse',
    '--format=format:'+commit_format,
    '..'.join(commit_range), '--',
])

commits = yaml.load(gitlog)

# what?  how can we have no commits?
if not commits:
    sys.exit()

p = re.compile(r'^Signed-off-by: ([^<]+) <([^<>@]+@[^<>]+)>$',
               re.MULTILINE | re.UNICODE)

failed_commits = []

for commit in commits:
    commit['message'] = commit['message'][1:]
    # trim off our '.' that exists just to prevent fun YAML parsing issues
    # see https://github.com/dotcloud/docker/pull/3836#issuecomment-33723094
    # and https://travis-ci.org/dotcloud/docker/builds/17926783

    commit['stat'] = subprocess.check_output([
        'git', 'log', '--format=format:', '--max-count=1',
        '--name-status', commit['hash'], '--',
    ])

    if commit['stat'] == '':
        print('Commit {0} has no changed content, '
              'skipping.'.format(commit['hash']))
        continue

    m = p.search(commit['message'])

    if not m:
        failed_commits.append(commit['hash'])
        continue

# print all failed commits
if failed_commits:
    print('{0} commit(s) have not been signed off:'
          .format(len(failed_commits)))
    print('\n'.join(failed_commits))
    sys.exit(1)

print('All commits have been signed off.')
