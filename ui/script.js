document.addEventListener('DOMContentLoaded', async function () {
    await loadConfig();
});

async function loadConfig() {
    try {
        const response = await fetch('/config');
        const data = await response.json();
        document.getElementById('chat-rules').value = data.chat_rules.join('\n');
        document.getElementById('warnings-before-ban').value = data.warnings_before_ban;
        document.getElementById('ignore-broadcaster').checked = data.ignore_broadcaster || false;
        document.getElementById('ignore-mods').checked = data.ignore_mods || false;
    } catch (error) {
        showNotification('Failed to load configuration. Please try again later.', 'red');
    }
}

async function updateConfig() {
    const config = {
        chat_rules: document.getElementById('chat-rules').value.split('\n'),
        warnings_before_ban: document.getElementById('warnings-before-ban').value,
        ignore_broadcaster: document.getElementById('ignore-broadcaster').checked,
        ignore_mods: document.getElementById('ignore-mods').checked
    };

    try {
        const response = await fetch('/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        const data = await response.json();
        showNotification(data.message, 'green');
    } catch (error) {
        showNotification('Failed to update configuration. Please try again later.', 'red');
    }
}

function showNotification(message, color) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.remove('hidden');
    notification.classList.replace('bg-green-500', color === 'green' ? 'bg-green-500' : 'bg-red-500');

    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
