#!/bin/bash

# Create the generated directory if it doesn't exist
mkdir -p generated

# Generate JavaScript code using protoc
protoc \
  --plugin=protoc-gen-grpc-web=./node_modules/.bin/protoc-gen-grpc-web \
  --js_out=import_style=commonjs:./generated \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:./generated \
  taskmanager.proto