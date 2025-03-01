# gRPC Task Manager

A simple task management application using gRPC for communication between the client and server.

## Project Overview

This project demonstrates the use of gRPC and gRPC-Web for communication between a Node.js server and a web client. The application allows users to:

- Add new tasks
- Retrieve task details
- List all tasks
- Delete tasks

## Prerequisites

Before running this project, ensure you have the following installed:

- [Node.js](https://nodejs.org/) (version 14 or higher)
- [Protocol Buffers Compiler (protoc)](https://github.com/protocolbuffers/protobuf/releases)

## Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

## Building the Project

1. Generate JavaScript files from proto definitions:

```bash
npm run proto:generate
```

2. Build the client-side JavaScript:

```bash
npm run build
```

For development with automatic rebuilding:

```bash
npm run dev:build
```

## Running the Application

Start both the gRPC server and the proxy server with a single command:

```bash
npm start
```

Alternatively, you can start the servers separately:

```bash
# Start the gRPC server
npm run start:server

# Start the proxy server
npm run start:proxy
```

Then open your browser and navigate to [http://localhost:8080](http://localhost:8080) to see the application.

## Project Structure

- `taskmanager.proto` - Protocol Buffers definition file
- `server.js` - gRPC server implementation
- `client.js` - Client-side JavaScript for interacting with the gRPC server
- `proxy.js` - gRPC-Web proxy server using Express
- `client.html` - Web interface
- `webpack.config.js` - Webpack configuration for bundling client-side JavaScript
- `scripts/generate-proto.js` - Script for generating JavaScript files from proto definitions
