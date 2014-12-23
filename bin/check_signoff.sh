#!/bin/bash

VALIDATE_REPO='https://github.com/chop-dbhi/avocado.git'
VALIDATE_BRANCH='master'

if [ -z "$VALIDATE_UPSTREAM" ]; then
    # this is kind of an expensive check, so let's not do this twice if we
    # are running more than one validate bundlescript
       
    if [ "$TRAVIS" = 'true' -a "$TRAVIS_PULL_REQUEST" != 'false' ]; then
        VALIDATE_REPO="https://github.com/${TRAVIS_REPO_SLUG}.git"
        VALIDATE_BRANCH="${TRAVIS_BRANCH}"
    fi
    
    VALIDATE_HEAD="$(git rev-parse --verify HEAD)"
    
    git fetch -q "$VALIDATE_REPO" "refs/heads/$VALIDATE_BRANCH"
    VALIDATE_UPSTREAM="$(git rev-parse --verify FETCH_HEAD)"
    
    VALIDATE_COMMIT_LOG="$VALIDATE_UPSTREAM..$VALIDATE_HEAD"
    VALIDATE_COMMIT_DIFF="$VALIDATE_UPSTREAM...$VALIDATE_HEAD"
    
    validate_diff() {
        if [ "$VALIDATE_UPSTREAM" != "$VALIDATE_HEAD" ]; then
            git diff "$VALIDATE_COMMIT_DIFF" "$@"
        fi
    }
    validate_log() {
        if [ "$VALIDATE_UPSTREAM" != "$VALIDATE_HEAD" ]; then
            git log "$VALIDATE_COMMIT_LOG" "$@"
        fi
    }
fi

adds=$(validate_diff --numstat | awk '{ s += $1 } END { print s }')
dels=$(validate_diff --numstat | awk '{ s += $2 } END { print s }')

: ${adds:=0}
: ${dels:=0}

dcoPrefix='Signed-off-by:'

check_dco() {
    grep -qE "$dcoPrefix"
}

if [ $adds -eq 0 -a $dels -eq 0 ]; then
    echo '0 adds, 0 deletions; nothing to validate!'
else
    commits=( $(validate_log --format='format:%H%n') )
    badCommits=()

    for commit in "${commits[@]}"; do
        if [ -z "$(git log -1 --format='format:' --name-status "$commit")" ]; then
            # no content (ie, Merge commit, etc)
            continue
        fi
        if ! git log -1 --format='format:%B' "$commit" | check_dco; then
            badCommits+=( "$commit" )
        fi
    done
    if [ ${#badCommits[@]} -eq 0 ]; then
        echo "Congratulations!  All commits are properly signed off!"
    else
        {
            echo "These commits do not have a proper '$dcoPrefix' marker:"
            for commit in "${badCommits[@]}"; do
                echo " - $commit"
            done
            echo
            echo 'Please amend each commit with a sign-off.'
            echo
        } >&2
        false
    fi
fi
