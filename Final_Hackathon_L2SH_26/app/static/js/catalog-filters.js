const categoryChips = Array.from(document.querySelectorAll(".check-chip"));
const allCategoriesLink = document.querySelector("[data-all-categories]");
const catalogFilterForm = document.querySelector(".catalog-filter-form");
const viewInputs = Array.from(document.querySelectorAll("input[name='view']"));

function syncAllCategoriesState() {
    const hasSelected = categoryChips.some((chip) => {
        const input = chip.querySelector("input[type='checkbox']");
        return input?.checked;
    });
    allCategoriesLink?.classList.toggle("active", !hasSelected);
}

function setChipState(chip, checked) {
    const input = chip.querySelector("input[type='checkbox']");
    if (!input) return;
    input.checked = checked;
    chip.classList.toggle("active", checked);
    syncAllCategoriesState();
}

categoryChips.forEach((chip) => {
    const input = chip.querySelector("input[type='checkbox']");
    if (!input) return;

    chip.addEventListener("click", (event) => {
        event.preventDefault();
        setChipState(chip, !input.checked);
    });

    chip.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        setChipState(chip, !input.checked);
    });

    setChipState(chip, input.checked);
});

allCategoriesLink?.addEventListener("click", (event) => {
    event.preventDefault();
    categoryChips.forEach((chip) => setChipState(chip, false));
});

allCategoriesLink?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    categoryChips.forEach((chip) => setChipState(chip, false));
});

viewInputs.forEach((input) => {
    input.addEventListener("change", () => {
        catalogFilterForm?.requestSubmit();
    });
});

catalogFilterForm?.addEventListener("submit", () => {
    categoryChips.forEach((chip) => {
        const input = chip.querySelector("input[type='checkbox']");
        if (input) {
            input.checked = chip.classList.contains("active");
        }
    });
});
