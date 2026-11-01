#!/bin/bash

cd backend

# docker run --name qa_backend_db -p 127.0.0.1:5532:5432 -e POSTGRES_PASSWORD=Examplepass17837 -d  postgres:15.4-bookworm

export POSTGRES_PASSWORD="Examplepass17837"
export POSTGRES_HOST="127.0.0.1"
export POSTGRES_PORT="5532"
export PYTHONPATH=.
flask run --reload