
import { getCookie } from './utils.js'; // Assuming utils.js is in the same directory

    const API_BASE_URL = ''; // Replace with your backend API base URL if necessary

    export function getAuthToken() {
        return localStorage.getItem('authToken');
    }

    export function getUserData() {
        const userData = localStorage.getItem('userData');
        if (userData) {
            try {
                return JSON.parse(userData);
            } catch (e) {
                console.error('Error parsing user data:', e);
                return null;
            }
        }
        return null;
    }

    export async function login(username, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/login/`, { // Confirm this URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ username: username, password: password })
            });

            const data = await response.json();

            if (response.ok) {
                alert('Login successful!');
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('userData', JSON.stringify(data.user));

                // Redirect based on user role
                const userRole = data.user.role; // Assuming role is in user data
                if (userRole === 'admin') {
                    window.location.href = '/admin/'; // Confirm admin dashboard URL
                } else if (userRole === 'faculty') {
                    window.location.href = '/faculty.html'; // Confirm faculty dashboard URL
                } else {
                    window.location.href = '/dash.html'; // Confirm student/default dashboard URL
                }
            } else {
                alert('Login failed: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('An error occurred during login.');
        }
    }
// Add these functions to your auth.js (or dashboard.js) file

    // Function to fetch Academic Events
    export async function fetchAcademicEvents() {
        const token = getAuthToken(); // Get token from localStorage

        if (!token) {
            console.warn("No auth token found. Cannot fetch academic events.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/academic-events/`, { // Confirm this URL and add filters if needed (e.g., ?date__gte=today)
                method: 'GET',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                 console.error('Error fetching academic events:', response.status, errorData);
                // Handle specific errors (e.g., 401 Unauthorized)
                 if (response.status === 401) {
                     // Redirect to login or show re-login prompt
                      console.log("Unauthorized. Please log in again.");
                     // logout(); // You might want to automatically log out
                 }
                 return []; // Return empty array on error
            }

            const events = await response.json();
            console.log("Fetched academic events:", events);
            return events;

        } catch (error) {
            console.error('Error fetching academic events:', error);
             // Display an error message on the page
            return []; // Return empty array on error
        }
    }

    // Function to fetch Notices (potentially used for tips)
    export async function fetchNotices() {
        const token = getAuthToken(); // Get token from localStorage

         if (!token) {
            console.warn("No auth token found. Cannot fetch notices.");
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/notices/`, { // Confirm this URL and add filters if needed
                method: 'GET',
                headers: {
                     'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 console.error('Error fetching notices:', response.status, errorData);
                  if (response.status === 401) {
                      console.log("Unauthorized. Please log in again.");
                  }
                return []; // Return empty array on error
            }

            const notices = await response.json();
             console.log("Fetched notices:", notices);
            return notices;

        } catch (error) {
            console.error('Error fetching notices:', error);
             return []; // Return empty array on error
        }
    }

    // Function to fetch Student Attendance Summary
     export async function fetchAttendanceSummary() {
        const token = getAuthToken(); // Get token from localStorage

         if (!token) {
            console.warn("No auth token found. Cannot fetch attendance summary.");
            return null; // Return null on error
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/student/attendance-summary/`, { // Confirm this URL
                method: 'GET',
                headers: {
                     'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 console.error('Error fetching attendance summary:', response.status, errorData);
                  if (response.status === 401) {
                      console.log("Unauthorized. Please log in again.");
                  }
                return null; // Return null on error
            }

            const summary = await response.json();
             console.log("Fetched attendance summary:", summary);
            return summary;

        } catch (error) {
            console.error('Error fetching attendance summary:', error);
            return null; // Return null on error
        }
    }

    // Placeholder function to fetch Today's Schedule (assuming a new backend endpoint)
    export async function fetchTodaySchedule() {
         const token = getAuthToken(); // Get token from localStorage

         if (!token) {
            console.warn("No auth token found. Cannot fetch today's schedule.");
            return null; // Return null on error
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/student/today-schedule/`, { // CONFIRM THIS URL
                method: 'GET',
                headers: {
                     'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                 const errorData = await response.json();
                 console.error('Error fetching today\'s schedule:', response.status, errorData);
                  if (response.status === 401) {
                      console.log("Unauthorized. Please log in again.");
                  }
                return null; // Return null on error
            }

            const schedule = await response.json();
             console.log("Fetched today's schedule:", schedule);
            return schedule; // Assuming schedule is an array of schedule items

        } catch (error) {
            console.error('Error fetching today\'s schedule:', error);
            return null; // Return null on error
        }
    }

    export function logout() {
        const token = getAuthToken();

        // Clear client-side storage immediately
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
        // sessionStorage.clear(); // If you use sessionStorage

        if (token) {
            fetch(`${API_BASE_URL}/api/auth/logout/`, { // Confirm this URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Token ${token}`,
                    'X-CSRFToken': getCookie('csrftoken') // Include if your logout also needs CSRF
                }
            })
            .then(response => {
                if (response.ok) {
                    console.log('Successfully logged out from backend.');
                } else {
                    console.warn('Backend logout call failed or user was not authenticated. Status:', response.status);
                }
            })
            .catch(error => {
                console.error('Error during logout API call:', error);
            })
            .finally(() => {
                // Always redirect after attempting backend logout and clearing local storage
                 window.location.href = '/login.html'; // Confirm login page URL
            });
        } else {
             // If no token was found, just redirect after clearing local storage
             console.log('No auth token found in localStorage. Proceeding with client-side cleanup and redirect.');
             window.location.href = '/login.html'; // Confirm login page URL
        }
    }

    export function checkAuthAndRedirect() {
        const token = getAuthToken();
        const userData = getUserData();
        const publicPages = ['login.html', 'signup.html']; // Add other public pages
        const currentPage = window.location.pathname.split('/').pop();

        if (!token && !publicPages.includes(currentPage)) {
            console.log('No token found and not on a public page. Redirecting to login.');
            window.location.href = '/login.html'; // Confirm login page URL
            return false; // Indicate not authenticated
        }

        if (token && userData) {
            console.log('User authenticated:', userData);
            // User is authenticated, you can update UI here
            // For example, display username, change login/signup to logout
            return true; // Indicate authenticated
        } else if (token && !userData && !publicPages.includes(currentPage)){
             // Token exists but no user data, something is wrong, try to logout / clear
            console.warn("Token found but no user data. Clearing token and redirecting to login.");
            localStorage.removeItem('authToken');
            window.location.removeItem('userData');
            window.location.href = '/login.html'; // Confirm login page URL
            return false; // Indicate not authenticated
        }

        return false; // Default to not authenticated if none of the above
    }


    // You might want to call checkAuthAndRedirect on DOMContentLoaded for protected pages
    // Example in a protected page's script:
    // document.addEventListener('DOMContentLoaded', () => {
    //     checkAuthAndRedirect();
    //     // If checkAuthAndRedirect returns true, proceed with page logic
    // });
