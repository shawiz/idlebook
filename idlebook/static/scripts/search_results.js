function saveOwnWish(button, copy_id) {
    if (copy_id != null && copy_id != -1) {
        openModal(copy_id);
    } else {
        button.removeClass('active');        
    }
}

function saveCopyEdit() {
    $.modal.close();
}