@echo off
REM Create the generated directory if it doesn't exist
if not exist generated mkdir generated

REM Generate JavaScript code using grpc-tools
npx grpc_tools_node_protoc ^
--js_out=import_style=commonjs,binary:./generated ^
--grpc_out=grpc_js:./generated ^
--proto_path=. ^
taskmanager.proto