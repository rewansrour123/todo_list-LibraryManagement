
document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");

    // Update button text based on current theme
    function updateThemeButton() {
        if (!themeToggle) return;

        const isDark = document.body.classList.contains("dark-mode");

        themeToggle.textContent = isDark
            ? "☀️ Light Mode"
            : "🌙 Dark Mode";
    }

    // Apply saved theme
    function applySavedTheme() {
        const savedTheme = localStorage.getItem("theme");

        document.body.classList.toggle(
            "dark-mode",
            savedTheme === "dark"
        );

        updateThemeButton();
    }

    // Toggle between light and dark mode
    if (themeToggle) {
        themeToggle.addEventListener("click", function () {

            const isDark =
                !document.body.classList.contains("dark-mode");

            document.body.classList.toggle("dark-mode", isDark);

            localStorage.setItem(
                "theme",
                isDark ? "dark" : "light"
            );

            updateThemeButton();
        });
    }

    applySavedTheme();

});
