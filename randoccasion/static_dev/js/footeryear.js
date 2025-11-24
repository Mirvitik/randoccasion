(function() {
    const yearElement = document.getElementById('year-footer');
    const serverTime = new Date(yearElement.dataset.serverTime);
    const clientTime = new Date();
    const timeDiInHours = Math.abs(serverTime - clientTime) / (1000 * 60 * 60);
    if (timeDiInHours > 24) {
        return;
    }
    const clientYear = clientTime.getFullYear();
    document.getElementById('year-footer').textContent = '© ' + clientYear;
})();
