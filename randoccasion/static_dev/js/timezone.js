(function() {
    function setTimezoneCookie() {
        const offset = new Date().getTimezoneOffset();
        const expiryDate = new Date();
        expiryDate.setFullYear(expiryDate.getFullYear() + 1);

        document.cookie = `timezone_offset=${offset}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
    }

    function hasTimezoneCookie() {
        return document.cookie.split(';').some(item => item.trim().startsWith('timezone_offset='));
    }

    if (!hasTimezoneCookie()) {
        setTimezoneCookie();
    }
})();