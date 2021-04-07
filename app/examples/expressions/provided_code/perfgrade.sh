#!/bin/sh
exec venv-run --venv /opt/perfgrade -- perfgrade "$@"
