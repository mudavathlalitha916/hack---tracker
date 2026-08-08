const signupForm = document.getElementById("signupForm");
const loginForm = document.getElementById("loginForm");
const signupError = document.getElementById("signupError");
const loginError = document.getElementById("loginError");

function showError(container, message) {
  if (container) {
    container.textContent = message;
  } else {
    alert(message);
  }
}

async function postJson(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  const payload = await response.json().catch(() => ({}));
  return { ok: response.ok, status: response.status, payload };
}

if (signupForm) {
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const name = document.getElementById("signupName").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value.trim();

    const { ok, payload } = await postJson("/api/signup", { name, email, password });
    if (!ok) {
      showError(signupError, payload.error || "Unable to create account.");
      return;
    }

    window.location.href = "/step2";
  });
}

if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    const { ok, payload } = await postJson("/api/login", { email, password });
    if (!ok) {
      showError(loginError, payload.error || "Invalid email or password.");
      return;
    }

    localStorage.setItem("currentHackathonUser", JSON.stringify(payload.user));
    window.location.href = "/step3";
  });
}
