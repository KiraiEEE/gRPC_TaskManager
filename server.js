const express = require('express');
const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');

// Express app setup
const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// gRPC setup
const PROTO_PATH = './taskmanager.proto';
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const taskProto = grpc.loadPackageDefinition(packageDefinition);
const tasks = new Map();

// gRPC service implementation
const server = new grpc.Server();
server.addService(taskProto.taskmanager.TaskManager.service, {
    addTask: (call, callback) => {
        const task = {
            id: uuidv4(),
            title: call.request.title,
            description: call.request.description,
            status: call.request.status || 'Pending',
            createdAt: new Date().toISOString()
        };
        tasks.set(task.id, task);
        callback(null, { task, message: 'Task added successfully' });
    },

    getTask: (call, callback) => {
        const task = tasks.get(call.request.taskId);
        if (task) {
            callback(null, { task, message: 'Task found' });
        } else {
            callback({
                code: grpc.status.NOT_FOUND,
                details: 'Task not found'
            });
        }
    },

    listTasks: (_, callback) => {
        callback(null, { tasks: Array.from(tasks.values()) });
    },

    deleteTask: (call, callback) => {
        if (tasks.delete(call.request.taskId)) {
            callback(null, { success: true, message: 'Task deleted' });
        } else {
            callback({
                code: grpc.status.NOT_FOUND,
                details: 'Task not found'
            });
        }
    },

    updateTask: (call, callback) => {
        const taskId = call.request.taskId;
        const task = tasks.get(taskId);
        
        if (!task) {
            callback({
                code: grpc.status.NOT_FOUND,
                details: 'Task not found'
            });
            return;
        }

        const updatedTask = {
            ...task,
            ...call.request.task,
            id: taskId // Ensure ID doesn't change
        };

        tasks.set(taskId, updatedTask);
        callback(null, { task: updatedTask, message: 'Task updated successfully' });
    }
});

// Start gRPC server
const grpcPort = 50051;
server.bindAsync(`0.0.0.0:${grpcPort}`, grpc.ServerCredentials.createInsecure(), (error, port) => {
    if (error) {
        console.error('Failed to bind gRPC server:', error);
        process.exit(1);
    }
    console.log(`gRPC Server running at 0.0.0.0:${port}`);
    server.start();
});



















// Express API routes
app.get('/api/tasks', (req, res) => {
    const client = new taskProto.taskmanager.TaskManager(
        'localhost:50051',
        grpc.credentials.createInsecure()
    );
    client.listTasks({}, (err, response) => {
        if (err) {
            console.error('Error listing tasks:', err);
            return res.status(500).json({ error: 'Failed to list tasks' });
        }
        res.json(response);
    });
});

app.post('/api/tasks', (req, res) => {
    const client = new taskProto.taskmanager.TaskManager(
        'localhost:50051',
        grpc.credentials.createInsecure()
    );
    client.addTask(req.body, (err, response) => {
        if (err) {
            console.error('Error adding task:', err);
            return res.status(500).json({ error: 'Failed to add task' });
        }
        res.json(response);
    });
});

app.get('/api/tasks/:id', (req, res) => {
    const client = new taskProto.taskmanager.TaskManager(
        'localhost:50051',
        grpc.credentials.createInsecure()
    );
    client.getTask({ taskId: req.params.id }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            return res.status(500).json({ error: 'Failed to get task' });
        }
        res.json(response);
    });
});

app.put('/api/tasks/:id', (req, res) => {
    const client = new taskProto.taskmanager.TaskManager(
        'localhost:50051',
        grpc.credentials.createInsecure()
    );
    client.updateTask({
        taskId: req.params.id,
        task: req.body
    }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            return res.status(500).json({ error: 'Failed to update task' });
        }
        res.json(response);
    });
});

app.delete('/api/tasks/:id', (req, res) => {
    const client = new taskProto.taskmanager.TaskManager(
        'localhost:50051',
        grpc.credentials.createInsecure()
    );
    client.deleteTask({ taskId: req.params.id }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            return res.status(500).json({ error: 'Failed to delete task' });
        }
        res.json(response);
    });
});

// Start Express server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Web server running at http://localhost:${PORT}`);
});
