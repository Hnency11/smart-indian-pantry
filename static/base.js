// Shared JS for Smart Indian Pantry

const API_BASE = ''; // Use relative paths for Flask integration

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/auth';
}

// Check for token on protected pages
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const publicPages = ['/auth', '/']; // Allow Home and Auth pages without token
    const currentPage = window.location.pathname;

    // Strict redirect if no token and current page is not public
    if (!token && !publicPages.includes(currentPage)) {
        window.location.href = '/auth';
    }

    // Update Nav links based on auth status
    const navLinks = document.getElementById('nav-links');
    if (!navLinks) return;

    if (token) {
        navLinks.innerHTML = `
            <a href="/pantry-page" class="nav-link px-3 d-inline">My Pantry</a>
            <a href="/recipes-page" class="nav-link px-3 d-inline">Recipes</a>
            <button onclick="logout()" class="btn btn-outline-danger btn-sm rounded-pill ms-3">Logout</button>
        `;
    } else {
        navLinks.innerHTML = `
            <a href="/auth" class="btn btn-primary rounded-pill">Login / Register</a>
        `;
    }
});
