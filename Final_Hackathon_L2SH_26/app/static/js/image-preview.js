const modal = document.querySelector("[data-image-modal]");
const modalImage = document.querySelector("[data-image-target]");
const modalTitle = document.querySelector("[data-image-title]");
const modalClose = document.querySelector("[data-image-close]");

function closePreview() {
    if (modal && modal.open) {
        modal.close();
    }
}

document.addEventListener("click", (event) => {
    const previewButton = event.target.closest("[data-preview-src]");
    if (!previewButton || !modal || !modalImage) return;

    modalImage.src = previewButton.dataset.previewSrc;
    modalImage.alt = previewButton.dataset.previewTitle || "Предпросмотр изображения";
    if (modalTitle) {
        modalTitle.textContent = previewButton.dataset.previewTitle || "Предпросмотр";
    }
    modal.showModal();
});

if (modalClose) {
    modalClose.addEventListener("click", closePreview);
}

if (modal) {
    modal.addEventListener("click", (event) => {
        if (event.target === modal) closePreview();
    });
}

