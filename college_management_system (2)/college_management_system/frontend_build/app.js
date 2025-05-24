import React, { useState, useEffect } from "react";



function App() {
  const [attendance, setAttendance] = useState(85);
  const [events, setEvents] = useState([
    { date: "March 15", event: "Sports Day" },
    { date: "March 20", event: "Science Fair" },
    { date: "March 25", event: "Parent Meeting" },
  ]);

  const [helpRequest, setHelpRequest] = useState({
    subject: "",
    message: "",
  });

  const handleHelpSubmit = (e) => {
    e.preventDefault();
    alert("Your help request has been submitted!");
    setHelpRequest({ subject: "", message: "" });
  };

  return (
    <div className="container-fluid">
      <div className="row">
        {/* Sidebar */}
        <div
          className="col-md-3 col-lg-2 sidebar"
          style={{ background: "linear-gradient(45deg, #343a40, #1a1c20)" }}
        >
          <div className="profile-section text-center py-4">
            <img
              src="teacher.png"
              alt="Profile"
              className="profile-img"
              style={{ border: "3px solid #4e73df" }}
            />
            <h5 style={{ color: "#4e73df" }}>Vasavi</h5>
          </div>
          <nav className="nav flex-column">
            <a className="nav-link" href="dash.html" style={{ color: "#36b9cc" }}>
              <i className="fa fa-home"></i> Dashboard
            </a>
            <a className="nav-link" href="schedule.html" style={{ color: "#1cc88a" }}>
              <i className="fa fa-calendar"></i> Schedule
            </a>
            <a className="nav-link" href="faculty.html" style={{ color: "#f6c23e" }}>
              <i className="fa fa-users"></i> Faculty
            </a>
            <a className="nav-link" href="sports.html" style={{ color: "#e74a3b" }}>
              <i className="fa fa-running"></i> Sports
            </a>
            <a className="nav-link" href="club.html" style={{ color: "#64b188" }}>
              <i className="fa fa-club"></i> Clubs
            </a>
            <a className="nav-link" href="academic.html" style={{ color: "#4e73df" }}>
              <i className="fa fa-calendar-alt"></i> Academic Calendar
            </a>
            <a className="nav-link" href="attendance.html" style={{ color: "#1cc88a" }}>
              <i className="fa fa-clipboard-check"></i> Attendance
            </a>
            <a className="nav-link" href="exam.html" style={{ color: "#36b9cc" }}>
              <i className="fa fa-file-alt"></i> Exams
            </a>
            <a className="nav-link" href="fee.html" style={{ color: "#f6c23e" }}>
              <i className="fa fa-dollar-sign"></i> Fee Payments
            </a>
            <a className="nav-link" href="notice.html" style={{ color: "#e74a3b" }}>
              <i className="fa fa-bullhorn"></i> Notice Board
            </a>
            <a className="nav-link" href="logout.html" style={{ color: "#858796" }}>
              <i className="fa fa-sign-out-alt"></i> Logout
            </a>
          </nav>
        </div>

        {/* Main Content */}
        <div className="col-md-9 col-lg-10 main-content" style={{ background: "#f8f9fc" }}>
          {/* Top Navigation */}
          <nav
            className="navbar navbar-expand-lg navbar-light mb-4"
            style={{ background: "linear-gradient(90deg, #4e73df, #36b9cc)" }}
          >
            <div className="container-fluid">
              <form className="d-flex">
                <input
                  className="form-control me-2"
                  type="search"
                  placeholder="Search"
                />
                <button className="btn btn-light" type="submit">
                  Search
                </button>
              </form>
              <div className="d-flex">
                <button className="btn btn-light me-2">Login</button>
                <button className="btn btn-warning">Sign Up</button>
              </div>
            </div>
          </nav>

          {/* Dashboard Cards */}
          <div className="row">
            <div className="col-md-4">
              <div className="card" style={{ borderLeft: "4px solid #4e73df" }}>
                <div className="card-body">
                  <h5 className="card-title text-primary">Today's Schedule</h5>
                  <p className="card-text">Loading schedule...</p>
                  <button className="btn btn-primary">View Schedule</button>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card" style={{ borderLeft: "4px solid #1cc88a" }}>
                <div className="card-body">
                  <h5 className="card-title text-success">Attendance Overview</h5>
                  <p className="card-text">
                    Current attendance: <span>{attendance}%</span>
                  </p>
                  <div className="progress">
                    <div
                      className="progress-bar bg-success"
                      role="progressbar"
                      style={{ width: `${attendance}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card" style={{ borderLeft: "4px solid #36b9cc" }}>
                <div className="card-body">
                  <h5 className="card-title text-info">Upcoming Events</h5>
                  <ul className="list-unstyled">
                    {events.map((event, index) => (
                      <li key={index}>{`${event.event} - ${event.date}`}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Help Form */}
          <div className="row mt-4">
            <div className="col-md-6">
              <div className="card" style={{ borderLeft: "4px solid #e74a3b" }}>
                <div className="card-body">
                  <h5 className="card-title text-danger">Need Help?</h5>
                  <form onSubmit={handleHelpSubmit}>
                    <div className="mb-3">
                      <label className="form-label">Subject</label>
                      <input
                        type="text"
                        className="form-control"
                        value={helpRequest.subject}
                        onChange={(e) =>
                          setHelpRequest({ ...helpRequest, subject: e.target.value })
                        }
                        required
                      />
                    </div>
                    <div className="mb-3">
                      <label className="form-label">Message</label>
                      <textarea
                        className="form-control"
                        rows="3"
                        value={helpRequest.message}
                        onChange={(e) =>
                          setHelpRequest({ ...helpRequest, message: e.target.value })
                        }
                        required
                      ></textarea>
                    </div>
                    <button type="submit" className="btn btn-danger">
                      Submit
                    </button>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
