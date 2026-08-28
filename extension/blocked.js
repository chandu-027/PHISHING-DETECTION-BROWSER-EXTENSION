document.addEventListener("DOMContentLoaded", () => {
    // 1. Get the original URL from query parameters
    const params = new URLSearchParams(window.location.search);
    const originalUrl = params.get("url") || "";
    
    // Display URL
    const urlDisplayEl = document.getElementById("blocked-url");
    if (originalUrl) {
        urlDisplayEl.textContent = originalUrl;
    } else {
        urlDisplayEl.textContent = "Unknown location";
    }
    
    // 1b. Parse and display Explainable AI (XAI) reasons
    const reasonsParam = params.get("reasons") || "";
    const reasonsListEl = document.getElementById("xai-reasons");
    if (reasonsListEl) {
        reasonsListEl.innerHTML = "";
        try {
            if (reasonsParam) {
                const reasons = JSON.parse(reasonsParam);
                if (Array.isArray(reasons) && reasons.length > 0) {
                    reasons.forEach(reason => {
                        const li = document.createElement("li");
                        li.textContent = reason;
                        reasonsListEl.appendChild(li);
                    });
                } else {
                    const li = document.createElement("li");
                    li.textContent = "Structural anomalies matching phishing signature patterns.";
                    reasonsListEl.appendChild(li);
                }
            } else {
                const li = document.createElement("li");
                li.textContent = "Structural anomalies matching phishing signature patterns.";
                reasonsListEl.appendChild(li);
            }
        } catch (e) {
            console.error("Error parsing XAI reasons:", e);
            const li = document.createElement("li");
            li.textContent = "Lexical anomalies flagged in the URL path structure.";
            reasonsListEl.appendChild(li);
        }
    }
    
    // 2. Back to Safety button action
    const btnBack = document.getElementById("btn-back");
    btnBack.addEventListener("click", () => {
        // Go back in history if possible, otherwise close the tab or go to google
        if (window.history.length > 1) {
            window.history.back();
        } else {
            window.location.href = "https://www.google.com";
        }
    });
    
    // 3. Proceed Anyway button action
    const btnProceed = document.getElementById("btn-proceed");
    btnProceed.addEventListener("click", async () => {
        if (!originalUrl) return;
        
        // Add original URL to whitelist in local storage
        const data = await chrome.storage.local.get("whitelist");
        const whitelist = data.whitelist || [];
        
        // Avoid duplicates
        if (!whitelist.includes(originalUrl)) {
            whitelist.push(originalUrl);
            await chrome.storage.local.set({ whitelist });
        }
        
        // Navigate to the original URL (will bypass interceptor now)
        window.location.href = originalUrl;
    });
});
