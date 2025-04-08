#!/bin/bash

# Trigger categorization
curl -X POST "http://localhost:8000/categorization/trigger" -H "accept: application/json"