(() => {
  const getStoredTheme = () => localStorage.getItem("theme");
  const setStoredTheme = theme => localStorage.setItem("theme", theme);

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
      return storedTheme;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  };

  const setTheme = theme => {
    document.documentElement.setAttribute("data-bs-theme", theme);
    updateThemeIcon(theme);
  };

  const updateThemeIcon = theme => {
    const themeIcon = document.querySelector(".theme-icon");
    if (themeIcon) {
      themeIcon.textContent = theme === "dark" ? "🌙" : "☀️";
    }
  };
  setTheme(getPreferredTheme());

  window.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
      themeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-bs-theme");
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        setStoredTheme(newTheme);
        setTheme(newTheme);
      });
    }

    updateThemeIcon(getPreferredTheme());
  });

  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", e => {
    const storedTheme = getStoredTheme();
    if (!storedTheme) {
      setTheme(e.matches ? "dark" : "light");
    }
  });
})();