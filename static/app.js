let hackathons = [];

async function loadHackathons() {
  try {
    const response = await fetch("/api/hackathons");
    if (!response.ok) {
      return;
    }
    hackathons = await response.json();
  } catch (error) {
    console.error("Failed to load hackathons:", error);
  }
}

const companyGrid = document.getElementById("companyGrid");
const hackathonGrid = document.getElementById("hackathonGrid");
const calendarGrid = document.getElementById("calendarGrid");
const notificationPanel = document.getElementById("notificationPanel");
const notificationToggle = document.getElementById("notificationToggle");
const companySearch = document.getElementById("companySearch");
const companyFilter = document.getElementById("companyFilter");
const dateFilter = document.getElementById("dateFilter");
const locationFilter = document.getElementById("locationFilter");
const authMessage = document.getElementById("authMessage");

const currentUserKey = "currentHackathonUser";
let currentUser = JSON.parse(localStorage.getItem(currentUserKey) || "null");

function getUniqueCompanies() {
  return [...new Set(hackathons.map((item) => item.company))].sort();
}

function getUniqueDates() {
  return [...new Set(hackathons.map((item) => item.date))].sort();
}

function getUniqueLocations() {
  return [...new Set(hackathons.map((item) => item.location))].sort();
}

function getSearchQuery() {
  return (companySearch?.value || "").trim().toLowerCase();
}

function populateFilters() {
  if (!companyFilter || !dateFilter || !locationFilter) return;

  companyFilter.innerHTML = `
    <option value="all">All companies</option>
    ${getUniqueCompanies().map((company) => `<option value="${company}">${company}</option>`).join("")}
  `;
  dateFilter.innerHTML = `
    <option value="all">All dates</option>
    ${getUniqueDates().map((date) => `<option value="${date}">${date}</option>`).join("")}
  `;
  locationFilter.innerHTML = `
    <option value="all">All locations</option>
    ${getUniqueLocations().map((location) => `<option value="${location}">${location}</option>`).join("")}
  `;
}

function getFilteredHackathons() {
  const query = getSearchQuery();
  const selectedCompany = companyFilter?.value || "all";
  const selectedDate = dateFilter?.value || "all";
  const selectedLocation = locationFilter?.value || "all";

  return hackathons.filter((item) => {
    const matchesSearch =
      item.company.toLowerCase().includes(query) ||
      item.name.toLowerCase().includes(query) ||
      item.details.toLowerCase().includes(query);

    const matchesCompany = selectedCompany === "all" || item.company === selectedCompany;
    const matchesDate = selectedDate === "all" || item.date === selectedDate;
    const matchesLocation = selectedLocation === "all" || item.location === selectedLocation;

    return matchesSearch && matchesCompany && matchesDate && matchesLocation;
  });
}

function renderCompanyList() {
  if (!companyGrid) return;

  const filteredHackathons = getFilteredHackathons();
  const companies = [...new Set(filteredHackathons.map((item) => item.company))].sort();

  if (!companies.length) {
    companyGrid.innerHTML = `
      <article class="card">
        <h3>No companies found</h3>
        <p>Try adjusting your search or filters to see matching companies and hackathons.</p>
      </article>
    `;
    return;
  }

  companyGrid.innerHTML = companies
    .map((company) => {
      const upcoming = filteredHackathons.filter((item) => item.company === company);
      return `
        <article class="card">
          <h3>${company}</h3>
          <div class="meta">
            <span class="tag">${upcoming[0].category}</span>
            <span class="tag">${upcoming.length} event${upcoming.length === 1 ? "" : "s"}</span>
            <span class="tag">${upcoming[0].location}</span>
          </div>
          <div class="event-list">
            ${upcoming
              .map(
                (item) => `
              <div class="event-row">
                <span class="event-name">${item.name}</span>
                <span>${item.date}</span>
                <span>${item.time}</span>
                <span>${item.location}</span>
                <span>${item.fee}</span>
              </div>
              <div class="event-details">${item.details}</div>
            `
              )
              .join("")}
          </div>
        </article>
      `;
    })
    .join("");
}

function renderHackathons() {
  if (!hackathonGrid) return;

  const results = getFilteredHackathons();

  if (!results.length) {
    hackathonGrid.innerHTML = `
      <article class="card">
        <h3>No matching hackathons</h3>
        <p>Try searching for a different company, date, or location.</p>
      </article>
    `;
    return;
  }

  hackathonGrid.innerHTML = results
    .map((item) => `
      <article class="card">
        <h3>${item.name}</h3>
        <div class="meta">
          <span class="tag">${item.company}</span>
          <span class="tag">${item.category}</span>
          <span class="tag">${item.duration}</span>
          <span class="tag">${item.fee}</span>
        </div>
        <p><strong>Date:</strong> ${item.date}</p>
        <p><strong>Time:</strong> ${item.time}</p>
        <p><strong>Location:</strong> ${item.location}</p>
        <p>${item.details}</p>
      </article>
    `)
    .join("");
}

function renderCalendar() {
  if (!calendarGrid) return;

  const events = getFilteredHackathons().sort((a, b) => a.date.localeCompare(b.date));

  if (!events.length) {
    calendarGrid.innerHTML = `
      <article class="card">
        <h3>No events to show</h3>
        <p>Change your search or filter settings to view hackathon dates.</p>
      </article>
    `;
    return;
  }

  const groupedByDate = events.reduce((grouped, item) => {
    grouped[item.date] = grouped[item.date] || [];
    grouped[item.date].push(item);
    return grouped;
  }, {});

  calendarGrid.innerHTML = Object.entries(groupedByDate)
    .map(([date, items]) => `
      <section class="calendar-day">
        <div class="calendar-day-header">
          <h3>${date}</h3>
          <span>${items.length} event${items.length === 1 ? "" : "s"}</span>
        </div>
        <div class="calendar-day-cards">
          ${items
            .map(
              (item) => `
            <article class="card calendar-card">
              <div class="meta">
                <span class="tag">${item.time}</span>
                <span class="tag">${item.duration}</span>
                <span class="tag">${item.location}</span>
                <span class="tag">${item.fee}</span>
              </div>
              <p><strong>${item.name}</strong></p>
              <p>${item.company} • ${item.category}</p>
              <p>${item.details}</p>
            </article>
          `
            )
            .join("")}
        </div>
      </section>
    `)
    .join("");
}

const notificationKey = "hackathonNotificationEnabled";

function getIndiaHackathons() {
  return hackathons.filter((item) => /\b(Bangalore|Mumbai|New Delhi|Delhi|Hyderabad|Chennai|Kolkata)\b/i.test(item.location));
}

function isNotificationEnabled() {
  return localStorage.getItem(notificationKey) === "enabled";
}

function setNotificationEnabled(value) {
  localStorage.setItem(notificationKey, value ? "enabled" : "disabled");
}

function requestNotificationPermission() {
  if (!("Notification" in window)) {
    alert("Browser notifications are not supported in this browser.");
    return Promise.resolve(false);
  }

  return Notification.requestPermission().then((permission) => permission === "granted");
}

function showBrowserNotification(message) {
  if (!("Notification" in window) || Notification.permission !== "granted") return;
  new Notification("Hackathon Tracker", {
    body: message,
    icon: "/static/icon.png"
  });
}

function renderNotificationPanel() {
  if (!notificationPanel) return;

  const indiaEvents = getIndiaHackathons();
  const enabled = isNotificationEnabled();
  const heading = enabled
    ? "Notifications enabled"
    : "Notifications disabled";
  const countText = indiaEvents.length
    ? `${indiaEvents.length} upcoming India hackathon${indiaEvents.length === 1 ? "" : "s"}`
    : "No India hackathons available right now.";

  notificationPanel.innerHTML = `
    <div class="notification-header">
      <div>
        <h2>${heading}</h2>
        <p>${countText}</p>
      </div>
      <button class="btn secondary" id="notificationToggle">${enabled ? "Turn off" : "Turn on"} notifications</button>
    </div>
    <div class="notification-list">
      ${indiaEvents
        .slice(0, 3)
        .map(
          (item) => `
          <div class="notification-item">
            <strong>${item.name}</strong>
            <span>${item.location} • ${item.date}</span>
          </div>
        `
        )
        .join("")}
    </div>
  `;

  const toggleButton = document.getElementById("notificationToggle");
  toggleButton?.addEventListener("click", () => {
    const currentlyEnabled = isNotificationEnabled();

    if (currentlyEnabled) {
      setNotificationEnabled(false);
      renderNotificationPanel();
      return;
    }

    requestNotificationPermission().then((granted) => {
      if (granted) {
        setNotificationEnabled(true);
        renderNotificationPanel();
        const message = indiaEvents.length
          ? `There are ${indiaEvents.length} new India hackathon${indiaEvents.length === 1 ? "" : "s"} available.`
          : "No India hackathons available yet, but we will notify you when one is added.";
        showBrowserNotification(message);
      } else {
        setNotificationEnabled(false);
        alert("Notifications were not granted. You can enable them again from the browser settings.");
        renderNotificationPanel();
      }
    });
  });
}

function updateUI() {
  renderCompanyList();
  renderHackathons();
  renderCalendar();
  renderNotificationPanel();
}

function attachSearchHandlers() {
  companySearch?.addEventListener("input", updateUI);
  companyFilter?.addEventListener("change", updateUI);
  dateFilter?.addEventListener("change", updateUI);
  locationFilter?.addEventListener("change", updateUI);
}

function attachAuthHandlers() {
  // This file no longer handles signup/login directly.
  // auth.js performs backend signup/login and persistence.
}

async function initializePage() {
  await loadHackathons();
  populateFilters();
  attachSearchHandlers();
  attachAuthHandlers();

  if (authMessage) {
    authMessage.textContent = currentUser
      ? `Welcome back, ${currentUser.name}! Start searching companies now.`
      : "Create an account or log in to unlock all features.";
  }

  updateUI();
}

initializePage();
