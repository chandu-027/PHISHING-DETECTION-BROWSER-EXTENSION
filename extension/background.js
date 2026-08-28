// Import the Decision Tree classifier rules
importScripts('predict_phishing.js');

// Real-time URL feature extraction logic in JavaScript
// This must align exactly with the Python extract_features.py pipeline.
function extractFeaturesFromUrl(urlString) {
    const urlStr = String(urlString);
    let hostname = "";
    
    try {
        let tempUrl = urlStr;
        // Ensure scheme is present for URL parser
        if (!/^[a-zA-Z]+:\/\//.test(tempUrl)) {
            tempUrl = 'http://' + tempUrl;
        }
        const urlObj = new URL(tempUrl);
        hostname = urlObj.hostname || "";
    } catch (e) {
        hostname = "";
    }

    // 1. Length features
    const url_length = urlStr.length;
    const domain_length = hostname.length;

    // 2. IP check
    const ipv4Pattern = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
    const is_ip = (ipv4Pattern.test(hostname) || hostname.includes(':')) ? 1 : 0;

    // 3. Count characters
    const qty_dot = (urlStr.split('.').length - 1);
    const qty_hyphen = (urlStr.split('-').length - 1);
    const qty_slash = (urlStr.split('/').length - 1);
    const qty_questionmark = (urlStr.split('?').length - 1);
    const qty_equal = (urlStr.split('=').length - 1);
    const qty_at = (urlStr.split('@').length - 1);
    const qty_and = (urlStr.split('&').length - 1);
    const qty_exclamation = (urlStr.split('!').length - 1);
    const qty_underline = (urlStr.split('_').length - 1);

    // 4. Protocol
    const is_https = urlStr.toLowerCase().startsWith('https') ? 1 : 0;

    // 5. Digits and letters
    let digits = 0;
    let letters = 0;
    for (let i = 0; i < urlStr.length; i++) {
        const c = urlStr[i];
        if (/[0-9]/.test(c)) {
            digits++;
        } else if (/[a-zA-Z]/.test(c)) {
            letters++;
        }
    }
    const qty_digits = digits;
    const qty_letters = letters;
    const digit_ratio = urlStr.length > 0 ? digits / urlStr.length : 0;

    // 6. Subdomain count
    let parts = hostname.split('.');
    if (parts.length > 0 && parts[0] === 'www') {
        parts = parts.slice(1);
    }
    const qty_subdomains = is_ip === 1 ? 0 : Math.max(0, parts.length - 2);

    // 7. Suspicious keywords
    const suspiciousWords = [
        'login', 'verify', 'secure', 'webscr', 'ebayisapi', 
        'signin', 'bank', 'account', 'update', 'free', 
        'bonus', 'paypal', 'wp-admin', 'verification'
    ];
    let has_suspicious_key = 0;
    const urlLower = urlStr.toLowerCase();
    for (const word of suspiciousWords) {
        if (urlLower.includes(word)) {
            has_suspicious_key = 1;
            break;
        }
    }

    return {
        url_length,
        domain_length,
        is_ip,
        qty_dot,
        qty_hyphen,
        qty_slash,
        qty_questionmark,
        qty_equal,
        qty_at,
        qty_and,
        qty_exclamation,
        qty_underline,
        is_https,
        qty_digits,
        qty_letters,
        digit_ratio,
        qty_subdomains,
        has_suspicious_key
    };
}

// Background Listener for Web Navigation in Manifest V3
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
    // Only intercept main frame navigation (frameId === 0)
    if (details.frameId !== 0) return;
    
    const url = details.url;
    const tabId = details.tabId;
    
    // Ignore internal chrome/extension pages
    if (
        url.startsWith("chrome://") || 
        url.startsWith("chrome-extension://") || 
        url.startsWith("about:") ||
        url.startsWith("edge://")
    ) {
        return;
    }
    
    // Retrieve configuration from local storage
    const data = await chrome.storage.local.get([
        "protectionEnabled", 
        "whitelist", 
        "blockedLogs", 
        "scannedCount", 
        "blockedCount"
    ]);
    
    const protectionEnabled = data.protectionEnabled !== false; // Default: true
    if (!protectionEnabled) return;
    
    // Check if whitelisted
    const whitelist = data.whitelist || [];
    if (whitelist.includes(url) || whitelist.some(w => url.startsWith(w))) {
        return;
    }
    
    // Increment scanned counter
    let scannedCount = data.scannedCount || 0;
    scannedCount++;
    await chrome.storage.local.set({ scannedCount });
    
    // Extract features and run prediction
    const features = extractFeaturesFromUrl(url);
    const prob = predictPhishing(features);
    
    // If prediction threshold is met
    if (prob >= 0.50) {
        // Increment blocked counter
        let blockedCount = data.blockedCount || 0;
        blockedCount++;
        
        // Explainable AI (XAI) Reason Diagnostics
        const reasons = [];
        if (features.is_https === 0) reasons.push("Unsecured protocol (HTTP is used instead of HTTPS)");
        if (features.has_suspicious_key === 1) reasons.push("Contains deceptive keywords (e.g., login, verify, signin, secure)");
        if (features.is_ip === 1) reasons.push("Identified by raw IP address rather than a registered domain name");
        if (features.qty_subdomains > 1) reasons.push(`Excessive subdomains detected (${features.qty_subdomains} subdomains)`);
        if (features.url_length > 40) reasons.push(`Web address is abnormally long (${features.url_length} characters)`);
        if (features.domain_length > 25) reasons.push(`Domain name length is suspicious (${features.domain_length} characters)`);
        if (features.qty_digits > 5) reasons.push(`High density of numbers in the path (${features.qty_digits} digits)`);
        if (features.qty_dot > 3) reasons.push(`Excessive separation dots in the URL structure (${features.qty_dot} dots)`);
        if (reasons.length === 0) reasons.push("Structural anomalies matching mathematical phishing signatures");

        const blockEvent = {
            url: url,
            prob: prob,
            reasons: reasons,
            time: new Date().toISOString()
        };

        // Log block event locally
        let blockedLogs = data.blockedLogs || [];
        blockedLogs.unshift(blockEvent);
        if (blockedLogs.length > 100) {
            blockedLogs = blockedLogs.slice(0, 100);
        }
        
        await chrome.storage.local.set({ blockedCount, blockedLogs });
        
        // Send block event to Flask Dashboard server (asynchronous, non-blocking)
        fetch("http://localhost:5000/api/log_block", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(blockEvent)
        }).catch(err => console.log("TrustNet Sync: Flask dashboard backend is offline"));

        // Redirect the user to the custom block warning page
        chrome.tabs.update(tabId, {
            url: chrome.runtime.getURL("blocked.html") + "?url=" + encodeURIComponent(url) + "&reasons=" + encodeURIComponent(JSON.stringify(reasons))
        });
    }
});
