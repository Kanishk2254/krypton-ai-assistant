// JARVIS-style JavaScript by Krypton AI Assistant

document.addEventListener('DOMContentLoaded', () => {
    const powerBtn = document.getElementById('power-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const stopBtn = document.getElementById('stop-btn');
    const sendBtn = document.getElementById('send-btn');
    const clearLogBtn = document.getElementById('clear-log');
    const commandInput = document.getElementById('command-input');
    const responseContent = document.getElementById('response-content');
    const commandsCount = document.getElementById('commands-count');
    const systemStatus = document.getElementById('system-status');
    const voiceMode = document.getElementById('voice-mode');
    const activityLog = document.getElementById('activity-log');
    const sessionInfo = document.getElementById('session-info');
    const cpuBar = document.getElementById('cpu-bar');
    const memoryBar = document.getElementById('memory-bar');
    const cpuValue = document.getElementById('cpu-value');
    const memoryValue = document.getElementById('memory-value');
    const currentTime = document.getElementById('current-time');
    const responseTime = document.getElementById('response-time');
    const loadingOverlay = document.getElementById('loading-overlay');

    // Helper functions for HTTP requests
    async function postData(url = '', data = {}) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        return response.json();
    }

    async function fetchJson(url) {
        const response = await fetch(url);
        return response.json();
    }

    // Button click handlers
    powerBtn.addEventListener('click', () => {
        const action = powerBtn.dataset.action;
        if (action === 'start') {
            postData('/api/start').then(data => {
                updateStatus(data.status);
            });
        }
    });

    voiceBtn.addEventListener('click', () => {
        const action = voiceBtn.dataset.action;
        if (action === 'voice') {
            postData('/api/voice/start').then(data => {
                updateStatus(data.status);
            });
        }
    });

    stopBtn.addEventListener('click', () => {
        postData('/api/stop').then(data => {
            updateStatus(data.status);
        });
    });

    sendBtn.addEventListener('click', () => {
        const command = commandInput.value.trim();
        if (!command) return;

        displayLoading(true);

        postData('/api/command', { command }).then(data => {
            displayResponse(command, data.response, data.timestamp);
            updateStatus(data.status);
            logActivity(command, data.response);
            displayLoading(false);
        });

        commandInput.value = '';
    });

    clearLogBtn.addEventListener('click', () => {
        activityLog.innerHTML = '';
    });

    // Add Enter key support for command input
    commandInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });

    // Periodic updates for system status
    setInterval(() => {
        fetchJson('/api/status').then(data => {
            updateStatus(data.krypton);
            updateSystemStats(data.system);
            currentTime.textContent = new Date().toLocaleTimeString();
        });
    }, 2000);

    // Helper functions
    function updateStatus(status) {
        systemStatus.textContent = status.active ? 'ONLINE' : 'OFFLINE';
        systemStatus.className = status.active ? 'status-value online' : 'status-value offline';
        sessionInfo.textContent = `Session: ${status.session_start || 'Not Active'}`;
        commandsCount.textContent = status.commands_processed || 0;

        if (status.active) {
            powerBtn.classList.add('disabled');
            voiceBtn.classList.remove('disabled');
            stopBtn.classList.remove('disabled');
            voiceMode.textContent = status.listening ? 'ACTIVE' : 'STANDBY';
        } else {
            powerBtn.classList.remove('disabled');
            voiceBtn.classList.add('disabled');
            stopBtn.classList.add('disabled');
            voiceMode.textContent = 'STANDBY';
        }
    }

    function updateSystemStats(system) {
        cpuBar.style.width = `${system.cpu_percent}%`;
        memoryBar.style.width = `${system.memory_percent}%`;
        cpuValue.textContent = `${system.cpu_percent}%`;
        memoryValue.textContent = `${system.memory_percent}%`;
    }

    function displayResponse(command, response, timestamp) {
        responseTime.textContent = new Date(timestamp).toLocaleTimeString();
        responseContent.innerHTML = `
            <div class="response">
                <div><strong>Command:</strong> ${command}</div>
                <div><strong>Response:</strong> ${response}</div>
            </div>`;
    }

    function logActivity(command, response) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = `
            <div class="log-entry">
                <span class="log-time">[${timestamp}]</span>
                <span class="log-message">
                    ${command} - <span>${response}</span>
                </span>
            </div>`;
        activityLog.innerHTML = logEntry + activityLog.innerHTML;
    }

    function displayLoading(show) {
        loadingOverlay.className = show ? 'loading-overlay' : 'loading-overlay hidden';
    }
});
