// frontend_build/static/js/auth.js

async function handleLogoutClick(event) {
    if(event) event.preventDefault(); // Prevent default link behavior if called from an anchor
    const token = localStorage.getItem('authToken');

    // Clear client-side storage immediately
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    // sessionStorage.clear(); // If you use sessionStorage

    if (token) {
        try {
            const response = await fetch('/api/auth/logout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                    'X-CSRFToken': getCookie('csrftoken') // Ensure getCookie is available
                }
            });
            if (response.ok) {
                console.log('Successfully logged out from backend.');
            } else {
                console.warn('Backend logout call failed. Status:', response.status);
            }
        } catch (error) {
            console.error('Error during logout API call:', error);
        }
    } else {
        console.log('No auth token found, already effectively logged out on client.');
    }
    // Redirect to login page
    window.location.href = '/login.html'; // Adjust if your login page URL is different
}

function checkAuth() {
    const token = localStorage.getItem('authToken');
    const userDataString = localStorage.getItem('userData');
    let userData = null;
    if (userDataString) {
        try {
            userData = JSON.parse(userDataString);
        } catch(e) {
            console.error("Error parsing user data from localStorage", e);
            localStorage.removeItem('userData'); // Clear corrupted data
            localStorage.removeItem('authToken'); // Assume logout if user data is bad
            window.location.href = 'login.html'; // Adjust to your login page URL
            return;
        }
    }

    const publicPages = ['login.html', 'signup.html'];
    // More robust way to get current page, handles query params etc.
    const currentPage = window.location.pathname.substring(window.location.pathname.lastIndexOf('/') + 1);


    if (!token && !publicPages.includes(currentPage)) {
        window.location.href = 'login.html'; // Adjust to your login page URL
        return;
    }

    const topNavAuthButtons = document.getElementById('topNavAuthButtons');
    const profileNameEl = document.querySelector('.sidebar .profile-section h5');

    if (token && userData) {
        if (profileNameEl) {
            profileNameEl.textContent = userData.first_name || userData.username;
        }

        if (topNavAuthButtons) {
            topNavAuthButtons.innerHTML = `
                <span class="navbar-text me-3 text-white">Welcome, ${userData.first_name || userData.username}!</span>
                <button class="btn btn-outline-light" id="dynamicLogoutBtnNav">Logout</button>
            `;
            const dynLogoutBtn = document.getElementById('dynamicLogoutBtnNav');
            if(dynLogoutBtn) dynLogoutBtn.addEventListener('click', handleLogoutClick);
        }

        // Conditional sidebar links (example)
        // Ensure your sidebar links have appropriate IDs or classes for targeting
        const userRole = userData.role;
        // Example: Hide faculty link for non-faculty
        const facultyLink = document.querySelector('.sidebar a[href*="faculty.html"]');
        if (facultyLink && userRole !== 'faculty' && userRole !== 'admin') {
            facultyLink.style.display = 'none';
        }
        // Add more role-based UI changes here

    } else if (token && !userData && !publicPages.includes(currentPage)) {
        console.warn("Token found but no user data. Clearing token and redirecting to login.");
        localStorage.removeItem('authToken');
        window.location.href = 'login.html'; // Adjust
    } else if (!token && topNavAuthButtons && publicPages.includes(currentPage)) {
         // On public pages, ensure login/signup buttons are shown if not logged in
        topNavAuthButtons.innerHTML = `
            <a href="login.html" class="btn btn-light me-2">Login</a>
            <a href="signup.html" class="btn btn-warning">Sign Up</a>
        `; // Adjust URLs
    }

    // Sidebar logout link functionality
    const sidebarLogoutLink = document.getElementById('sidebarLogoutLink');
    if(sidebarLogoutLink){
        sidebarLogoutLink.addEventListener('click', handleLogoutClick);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
});