// Date/time utilities

function getCurrentDatetime() {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const unixSeconds = Math.floor(now.getTime() / 1000);
    return `${dateStr}-${unixSeconds}`;
}
