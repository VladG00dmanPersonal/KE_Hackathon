const themeButton = document.querySelector("[data-theme-toggle]");

function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
    if (themeButton) {
        const isDark = theme === "dark";
        themeButton.setAttribute("aria-pressed", String(isDark));
        const label = isDark ? "Переключить на светлую тему" : "Переключить на тёмную тему";
        themeButton.setAttribute("aria-label", label);
        themeButton.setAttribute("title", label);
        themeButton.dataset.theme = theme;
    }
    window.dispatchEvent(new CustomEvent("themechange", { detail: { theme } }));
}

applyTheme(localStorage.getItem("theme") || document.documentElement.dataset.theme || "light");

if (themeButton) {
    themeButton.addEventListener("click", () => {
        applyTheme(document.documentElement.dataset.theme === "dark" ? "light" : "dark");
    });
}
