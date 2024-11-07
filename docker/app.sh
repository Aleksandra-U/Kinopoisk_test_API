#!/bin/bash

alembic upgrade head

gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
