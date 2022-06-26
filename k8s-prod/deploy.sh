#!/bin/bash -e
CURRENT_COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_HASH="${1:-$CURRENT_COMMIT_HASH}"

echo "Updating deployment image and run jobs for commit ${COMMIT_HASH}"
echo

cd `dirname "$0"`

for manifest in configmap.yaml healthpage.yaml cronjob.yaml
do
    cat $manifest | sed "s/<COMMIT_HASH>/$COMMIT_HASH/" | kubectl apply -f -
done

echo
echo "Project deployed successfully"
