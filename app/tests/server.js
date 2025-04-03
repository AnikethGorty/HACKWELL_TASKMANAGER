const express = require('express');
const WebSocket = require('ws');
const path = require('path');

const app = express();
const port = 3000;

// Serve static files
app.use(express.static(path.join(__dirname)));

// WebSocket server
const wss = new WebSocket.Server({ port: 8765 });

wss.on('connection', (ws) => {
  console.log('New client connected');
  ws.on('message', (message) => {
    console.log(`Received: ${message}`);
    ws.send(`Server received: ${message}`);
  });
});

// Start HTTP server
app.listen(port, () => {
  console.log(`HTTP server running on http://localhost:${port}`);
  console.log(`WebSocket server running on ws://localhost:8765`);
  console.log(`Open http://localhost:${port}/launcher.html in your browser`);
});