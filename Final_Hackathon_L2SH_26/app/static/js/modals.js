function closeDialog(dialog) {
    if (dialog && dialog.open) {
        dialog.close();
    }
}

const confirmDialog = document.querySelector("[data-confirm-dialog]");
const confirmHeading = confirmDialog?.querySelector("[data-confirm-heading]");
const confirmCopy = confirmDialog?.querySelector("[data-confirm-copy]");
const confirmAccept = confirmDialog?.querySelector("[data-confirm-accept]");
const confirmKicker = confirmDialog?.querySelector("[data-confirm-kicker]");
const confirmMark = confirmDialog?.querySelector("[data-confirm-mark]");
const confirmNote = confirmDialog?.querySelector("[data-confirm-note]");

let pendingConfirmation = null;
let previousFocus = null;

function getConfirmVariantMeta(variant) {
    if (variant === "danger") {
        return {
            kicker: "Опасное действие",
            mark: "!",
            note: "После подтверждения действие будет выполнено сразу. Отменить его потом не получится.",
        };
    }

    return {
        kicker: "Подтвердите действие",
        mark: "?",
        note: "Проверьте данные перед продолжением.",
    };
}

function closeConfirmDialog() {
    if (!confirmDialog?.open) {
        return;
    }

    closeDialog(confirmDialog);
    confirmDialog.removeAttribute("data-variant");
    confirmAccept?.removeAttribute("data-variant");
    pendingConfirmation = null;

    if (previousFocus instanceof HTMLElement) {
        previousFocus.focus();
    }
    previousFocus = null;
}

function openConfirmDialog(form, submitter) {
    if (!confirmDialog || !confirmHeading || !confirmCopy || !confirmAccept) {
        return false;
    }

    const message = form.dataset.confirmMessage?.trim();
    if (!message) {
        return false;
    }

    const variant = form.dataset.confirmVariant?.trim() || "default";
    const meta = getConfirmVariantMeta(variant);

    pendingConfirmation = { form, submitter };
    previousFocus = submitter instanceof HTMLElement ? submitter : document.activeElement;

    confirmDialog.dataset.variant = variant;
    confirmHeading.textContent = form.dataset.confirmTitle?.trim() || "Подтверждение";
    confirmCopy.textContent = message;
    if (confirmKicker) {
        confirmKicker.textContent = form.dataset.confirmKicker?.trim() || meta.kicker;
    }
    if (confirmMark) {
        confirmMark.textContent = form.dataset.confirmMark?.trim() || meta.mark;
    }
    if (confirmNote) {
        confirmNote.textContent = form.dataset.confirmNote?.trim() || meta.note;
    }
    confirmAccept.textContent = form.dataset.confirmConfirmLabel?.trim() || "Подтвердить";
    confirmAccept.dataset.variant = variant;

    if (!confirmDialog.open && confirmDialog.showModal) {
        confirmDialog.showModal();
    }

    confirmAccept.focus();
    return true;
}

document.addEventListener("submit", (event) => {
    const form = event.target.closest("form[data-confirm-message]");
    if (!form) {
        return;
    }

    if (form.dataset.confirmed === "true") {
        delete form.dataset.confirmed;
        return;
    }

    if (openConfirmDialog(form, event.submitter)) {
        event.preventDefault();
    }
});

confirmAccept?.addEventListener("click", () => {
    if (!pendingConfirmation) {
        return;
    }

    const { form, submitter } = pendingConfirmation;
    closeConfirmDialog();
    form.dataset.confirmed = "true";
    if (typeof form.requestSubmit === "function") {
        form.requestSubmit(submitter);
        return;
    }
    form.submit();
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && confirmDialog?.open) {
        event.preventDefault();
        closeConfirmDialog();
    }
});

document.addEventListener("click", (event) => {
    const confirmCancel = event.target.closest("[data-confirm-cancel]");
    if (confirmCancel) {
        closeConfirmDialog();
        return;
    }

    if (confirmDialog?.open && event.target === confirmDialog) {
        closeConfirmDialog();
        return;
    }

    const openButton = event.target.closest("[data-open-dialog]");
    if (openButton) {
        const dialog = document.getElementById(openButton.dataset.openDialog);
        if (dialog?.showModal) {
            dialog.showModal();
        }
        return;
    }

    const closeButton = event.target.closest("[data-close-dialog]");
    if (closeButton) {
        closeDialog(closeButton.closest("dialog"));
        return;
    }

    const dialog = event.target.closest("dialog.app-modal");
    if (dialog && event.target === dialog) {
        closeDialog(dialog);
    }
});
