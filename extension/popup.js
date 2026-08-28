document.addEventListener("DOMContentLoaded", async () => {
    const toggle = document.getElementById("protection-toggle");
    const themeToggle = document.getElementById("theme-toggle");
    const statScanned = document.getElementById("stat-scanned");
    const statBlocked = document.getElementById("stat-blocked");
    const logList = document.getElementById("log-list");
    const noLogsMsg = document.getElementById("no-logs-msg");
    const btnClearLogs = document.getElementById("btn-clear-logs");
    
    const statusText = document.getElementById("status-text");
    const statusPulse = document.getElementById("status-pulse");
    
    // Update dashboard statistics and logs from chrome.storage
    async function updateUI() {
        const data = await chrome.storage.local.get([
            "protectionEnabled", 
            "themeMode",
            "scannedCount", 
            "blockedCount", 
            "blockedLogs"
        ]);
        
        const enabled = data.protectionEnabled !== false;
        toggle.checked = enabled;
        
        // Sync theme class and toggle checkbox status
        const isDark = data.themeMode !== "light";
        themeToggle.checked = isDark;
        document.body.classList.toggle("light-mode", !isDark);
        
        // Update Active/Disabled badge
        if (enabled) {
            statusText.textContent = "Active";
            statusText.style.color = isDark ? "#00f2fe" : "#1d4ed8";
            statusPulse.style.backgroundColor = isDark ? "#00f2fe" : "#1d4ed8";
            statusPulse.style.boxShadow = isDark ? "0 0 8px #00f2fe" : "0 0 8px rgba(29, 78, 216, 0.4)";
            statusPulse.style.animation = "pulse 2s infinite";
        } else {
            statusText.textContent = "Disabled";
            statusText.style.color = "#8b9bb4";
            statusPulse.style.backgroundColor = "#8b9bb4";
            statusPulse.style.boxShadow = "none";
            statusPulse.style.animation = "none";
        }
        
        statScanned.textContent = data.scannedCount || 0;
        statBlocked.textContent = data.blockedCount || 0;
        
        const logs = data.blockedLogs || [];
        if (logs.length === 0) {
            logList.innerHTML = "";
            logList.appendChild(noLogsMsg);
        } else {
            logList.innerHTML = "";
            logs.forEach(log => {
                const item = document.createElement("div");
                item.className = "log-item";
                
                // Get domain name
                let domain = "";
                try {
                    const urlObj = new URL(log.url);
                    domain = urlObj.hostname;
                } catch(e) {
                    domain = log.url;
                }
                
                // Format time into readable format
                const date = new Date(log.time);
                const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                
                const percent = Math.round(log.prob * 100);
                
                item.innerHTML = `
                    <div class="log-details">
                        <span class="log-domain" title="${log.url}">${domain}</span>
                        <span class="log-time">${timeStr}</span>
                    </div>
                    <span class="log-badge">${percent}% Phish</span>
                `;
                logList.appendChild(item);
            });
        }
    }
    
    // Run initial UI update
    await updateUI();
    
    // Toggle state change handler
    toggle.addEventListener("change", async () => {
        const enabled = toggle.checked;
        await chrome.storage.local.set({ protectionEnabled: enabled });
        await updateUI();
    });
    
    // Theme toggle change handler
    themeToggle.addEventListener("change", async () => {
        const themeMode = themeToggle.checked ? "dark" : "light";
        await chrome.storage.local.set({ themeMode });
        await updateUI();
    });
    
    // Reset Data click handler
    btnClearLogs.addEventListener("click", async () => {
        if (confirm("Reset scanned stats, blocked threats, and whitelists?")) {
            await chrome.storage.local.set({
                scannedCount: 0,
                blockedCount: 0,
                blockedLogs: [],
                whitelist: []
            });
            await updateUI();
        }
    });
});
