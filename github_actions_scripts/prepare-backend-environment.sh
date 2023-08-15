#!/bin/bash
#prepare-backend-environment.sh
#Prepares the backend environment variable file.
#The deployment (using Okteto) requires an envfile
#dumped at /website/backend/backend.env.
#We dump all our secrets to there!
echo "Dumping backend environment variables..."
printenv > "./website/backend/backend.env" || exit 1
echo "Variables dumped to file."