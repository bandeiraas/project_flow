// frontend/js/logger.js

const LOG_KEY = 'appLogs';

// Limpa os logs antigos ao iniciar uma nova sessão de página
// (exceto se estivermos na página de visualização de logs)
if (!window.location.pathname.includes('debug_log.html')) {
    sessionStorage.removeItem(LOG_KEY);
}

function getLogs() {
    const logs = sessionStorage.getItem(LOG_KEY);
    return logs ? JSON.parse(logs) : [];
}

function saveLog(newLog) {
    const logs = getLogs();
    logs.push(newLog);
    sessionStorage.setItem(LOG_KEY, JSON.stringify(logs));
}

export const logger = {
    log: (message, ...data) => {
        const timestamp = new Date().toLocaleTimeString();
        console.log(message, ...data);
        saveLog({ level: 'LOG', timestamp, message, data });
    },
    warn: (message, ...data) => {
        const timestamp = new Date().toLocaleTimeString();
        console.warn(message, ...data);
        saveLog({ level: 'WARN', timestamp, message, data });
    },
    error: (message, ...data) => {
        const timestamp = new Date().toLocaleTimeString();
        console.error(message, ...data);
        saveLog({ level: 'ERROR', timestamp, message, data });
    }
};