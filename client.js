const express = require('express');
const path = require('path');
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname)));

const PROTO_PATH = './taskmanager.proto';

// Initialize gRPC client
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});
const taskProto = grpc.loadPackageDefinition(packageDefinition);
const client = new taskProto.taskmanager.TaskManager(
    '127.0.0.1:50051',
    grpc.credentials.createInsecure()
);

// API Routes
app.get('/api/tasks', (req, res) => {
    client.listTasks({}, (err, response) => {
        if (err) {
            console.error('Error listing tasks:', err);
            return res.status(500).json({ error: 'Failed to list tasks' });
        }
        res.json(response);
    });
});

app.post('/api/tasks', (req, res) => {
    client.addTask(req.body, (err, response) => {
        if (err) {
            console.error('Error adding task:', err);
            return res.status(500).json({ error: 'Failed to add task' });
        }
        res.json(response);
    });
});

app.get('/api/tasks/:id', (req, res) => {
    client.getTask({ taskId: req.params.id }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            console.error('Error getting task:', err);
            return res.status(500).json({ error: 'Failed to get task' });
        }
        res.json(response);
    });
});

app.put('/api/tasks/:id', (req, res) => {
    client.updateTask({
        taskId: req.params.id,
        task: req.body
    }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            console.error('Error updating task:', err);
            return res.status(500).json({ error: 'Failed to update task' });
        }
        res.json(response);
    });
});

app.delete('/api/tasks/:id', (req, res) => {
    client.deleteTask({ taskId: req.params.id }, (err, response) => {
        if (err) {
            if (err.code === grpc.status.NOT_FOUND) {
                return res.status(404).json({ error: 'Task not found' });
            }
            console.error('Error deleting task:', err);
            return res.status(500).json({ error: 'Failed to delete task' });
        }
        res.json(response);
    });
});

// Serve the HTML page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'client.html'));
});

// Start the server
const PORT = 8080;
app.listen(PORT, () => {
    console.log(`Web server running at http://localhost:${PORT}`);
});
