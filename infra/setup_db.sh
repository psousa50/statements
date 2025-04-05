#!/bin/bash

# Start the database
podman run -d --name postgres-bankstatements -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=bankstatements -p 5432:5432 postgres:14