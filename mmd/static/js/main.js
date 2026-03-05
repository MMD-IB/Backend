
document.addEventListener('DOMContentLoaded', function () {
    const avatarSpan = document.getElementById('sidebar_avatar');
    const nameEl = document.getElementById('sidebar_user_name');

    if (avatarSpan) {
        const name = avatarSpan.dataset.name || '';
        const surname = avatarSpan.dataset.surname || '';

        // Set initials in avatar circle
        const initials = (name.charAt(0) + surname.charAt(0)).toUpperCase();
        avatarSpan.textContent = initials || '?';

        // Set full name in sidebar text
        if (nameEl) {
            nameEl.textContent = name + (surname ? ' ' + surname : '');
        }
    }
});