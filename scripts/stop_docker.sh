#!/bin/bash

# Stop Docker container gracefully
docker stop tarafirst || true
docker rm tarafirst || true
