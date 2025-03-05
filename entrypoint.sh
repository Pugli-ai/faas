#!/bin/bash

# entrypoint.sh
echo "Running entrypoint.sh..."

# Get the passed environment variable argument
echo "Environment: $ENVIRONMENT"

if [ "$ENVIRONMENT" = "test" ]; then
  echo "Running tests..."
  /bin/bash startup-test.sh
else
  echo "Starting application..."
  /bin/bash startup.sh
fi