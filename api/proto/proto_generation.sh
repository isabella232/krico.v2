#!/bin/bash

python -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. api.proto
