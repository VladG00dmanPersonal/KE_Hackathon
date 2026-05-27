function currentTheme() {
    return document.documentElement.dataset.theme === "dark" ? "dark" : "light";
}

function refreshMatplotlibCharts() {
    const stamp = Date.now();
    document.querySelectorAll("[data-chart]").forEach((image) => {
        const kind = image.dataset.chart;
        image.src = `/stats/chart/${kind}.png?theme=${currentTheme()}&t=${stamp}`;
    });
}

refreshMatplotlibCharts();
setInterval(refreshMatplotlibCharts, 30000);
window.addEventListener("themechange", refreshMatplotlibCharts);
