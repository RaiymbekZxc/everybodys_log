const API_BASE = "https://everybodys-log.onrender.com";
const TOKEN_KEY = "access_token";

const categories = {
  1: { label: "Productivity", api: "productivity" },
  2: { label: "Social Life", api: "social-life" },
  3: { label: "Leisure", api: "leisure" },
};

const state = {
  user: null,
  posts: [],
  filter: "all",
  selectedCategory: null,
  existingPost: null,
  savingActivity: false,
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => Array.from(document.querySelectorAll(selector));

function getPage() {
  return document.body.dataset.page || "dashboard";
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function showStatus(message, type = "") {
  const status = $("#status");
  if (!status) return;
  status.textContent = message;
  status.className = `status ${type}`.trim();
}

function redirectToLogin() {
  window.location.href = "login.html";
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = typeof payload === "string"
      ? payload
      : payload.detail || JSON.stringify(payload);
    throw new Error(message);
  }

  return payload;
}

function bindLogout() {
  const button = $("#quickLogout");
  if (!button) return;

  button.addEventListener("click", wrap(async () => {
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } catch {
      // Local token removal still matters if the server rejects logout.
    }
    clearToken();
    redirectToLogin();
  }));
}

async function loadMe() {
  state.user = await apiFetch("/api/auth/users/me");

  const sessionStatus = $("#sessionStatus");
  if (sessionStatus) sessionStatus.textContent = `Signed in as ${state.user.Username}`;

  const profileId = $("#profileId");
  if (profileId) {
    profileId.textContent = `${state.user.UserId}${state.user.IsAdmin ? " *" : ""}`;
    $("#profileUsername").textContent = state.user.Username;
    $("#profileEmail").textContent = state.user.Email;
    $("#newUsername").value = state.user.Username;
  }

  return state.user;
}

async function requireAuth() {
  if (!getToken()) {
    redirectToLogin();
    return null;
  }

  try {
    return await loadMe();
  } catch (error) {
    clearToken();
    redirectToLogin();
    throw error;
  }
}

function setScore(prefix, score) {
  $(`#${prefix}Pct`).textContent = `${score?.percentage || 0}%`;
  $(`#${prefix}Count`).textContent = `${score?.count || 0} votes`;
}

async function loadDashboard() {
  const info = await apiFetch("/api/activity/info");
  $("#periodLabel").textContent = info.timestamp || "Current";
  setScore("productivity", info.productivity);
  setScore("social", info.social_life);
  setScore("leisure", info.leisure);
}

async function loadCategoryPosts(categoryApi) {
  const all = [];
  let page = 1;

  while (page < 25) {
    const batch = await apiFetch(`/api/posts/${categoryApi}?page=${page}`);
    all.push(...batch);
    if (batch.length < 5) break;
    page += 1;
  }

  return all;
}

async function loadPosts() {
  const [productivity, socialLife, leisure] = await Promise.all([
    loadCategoryPosts("productivity"),
    loadCategoryPosts("social-life"),
    loadCategoryPosts("leisure"),
  ]);

  state.posts = [...productivity, ...socialLife, ...leisure]
    .sort((a, b) => new Date(b.DateLogged) - new Date(a.DateLogged));
}

async function getUsername(userId) {
  try {
    const user = await apiFetch(`/api/posts/user/id/${userId}`);
    return user.Username;
  } catch {
    return `User ${userId}`;
  }
}

async function renderPosts() {
  const list = $("#postList");
  if (!list) return;

  const visible = state.posts.filter((post) => (
    state.filter === "all" || String(post.Activity) === state.filter
  ));

  list.replaceChildren();

  if (!visible.length) {
    const empty = document.createElement("div");
    empty.className = "panel";
    empty.textContent = "No posts found.";
    list.append(empty);
    return;
  }

  for (const post of visible) {
    const card = document.createElement("article");
    card.className = "post-card";

    const username = await getUsername(post.Author);
    const canDelete = state.user && post.Author === state.user.UserId;

    card.innerHTML = `
      <header>
        <strong></strong>
        <span class="tag"></span>
      </header>
      <p></p>
    `;

    card.querySelector("strong").textContent = username;
    card.querySelector(".tag").textContent = categories[post.Activity]?.label || "Unknown";
    card.querySelector("p").textContent = post.Text || "";

    if (canDelete) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "danger";
      button.textContent = "Delete My Post";
      button.addEventListener("click", wrap(deleteMyPost));
      card.append(button);
    }

    list.append(card);
  }
}

function selectCategory(category) {
  state.selectedCategory = category;
  $$(".category-btn").forEach((button) => {
    const active = button.dataset.category === category;
    button.classList.toggle("active", active);
    const img = button.querySelector("img");
    if (!img) return;
    const prefix = button.dataset.category === "social-life"
      ? "social_life"
      : button.dataset.category;
    img.src = `assets/images/${prefix}_${active ? "active" : "normal"}.png`;
  });
}

function updateCounter() {
  const text = $("#activityText");
  const counter = $("#charCounter");
  if (text && counter) counter.textContent = `${text.value.length}/100`;
}

function syncMyPost() {
  state.existingPost = state.posts.find((post) => (
    state.user && post.Author === state.user.UserId
  )) || null;

  if (state.existingPost) {
    selectCategory(categories[state.existingPost.Activity]?.api || null);
    $("#activityText").value = state.existingPost.Text || "";
    $("#deletePost").disabled = false;
    $$(".category-btn").forEach((button) => {
      button.disabled = true;
    });
    showStatus("You already have one entry. Editing will update that entry.", "success");
  } else {
    selectCategory(null);
    $("#activityText").value = "";
    $("#deletePost").disabled = true;
    $$(".category-btn").forEach((button) => {
      button.disabled = false;
    });
  }

  updateCounter();
}

async function saveActivity(event) {
  event.preventDefault();
  if (state.savingActivity) return;

  const text = $("#activityText").value.trim();
  const selectedCategory = state.selectedCategory;

  if (!selectedCategory) {
    showStatus("Choose an activity category.", "error");
    return;
  }
  if (!text) {
    showStatus("Write one sentence before saving.", "error");
    return;
  }

  state.savingActivity = true;

  try {
    await loadPosts();
    const existingPost = state.posts.find((post) => (
      state.user && post.Author === state.user.UserId
    )) || null;
    const category = existingPost
      ? categories[existingPost.Activity]?.api
      : selectedCategory;

    if (!category) {
      throw new Error("Could not resolve the activity category.");
    }

    if (existingPost) {
      await apiFetch("/api/posts/", { method: "DELETE" });
    } else {
      await apiFetch(`/api/activity/${category}`, { method: "POST" });
    }

    const params = new URLSearchParams({ text, category });
    await apiFetch(`/api/posts/activity?${params}`, { method: "POST" });
    await loadPosts();
    syncMyPost();
    showStatus("Activity entry saved.", "success");
  } finally {
    state.savingActivity = false;
  }
}

async function deleteMyPost() {
  await apiFetch("/api/posts/", { method: "DELETE" });
  await loadPosts();
  syncMyPost();
  await renderPosts();
  showStatus("Your post was deleted.", "success");
}

async function login(event) {
  event.preventDefault();
  const body = new URLSearchParams({
    username: $("#loginUsername").value.trim(),
    password: $("#loginPassword").value,
  });

  const data = await apiFetch("/api/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  setToken(data.access_token);
  window.location.href = "index.html";
}

async function register(event) {
  event.preventDefault();
  const username = $("#registerUsername").value.trim();
  const password = $("#registerPassword").value;

  await apiFetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      Username: username,
      Email: $("#registerEmail").value.trim(),
      Password: password,
      IsActive: true,
    }),
  });

  const body = new URLSearchParams({ username, password });
  const data = await apiFetch("/api/auth/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  setToken(data.access_token);
  window.location.href = "index.html";
}

async function updateUsername(event) {
  event.preventDefault();
  await apiFetch("/api/auth/users/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      TypeOfInteraction: "username",
      Username: $("#newUsername").value.trim(),
    }),
  });
  await loadMe();
  showStatus("Username updated.", "success");
}

async function updatePassword(event) {
  event.preventDefault();
  await apiFetch("/api/auth/users/me", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      TypeOfInteraction: "password",
      Password: $("#currentPassword").value,
      NewPassword: $("#newPassword").value,
    }),
  });
  $("#currentPassword").value = "";
  $("#newPassword").value = "";
  showStatus("Password updated.", "success");
}

async function runAdminAction(event) {
  event.preventDefault();
  const action = event.submitter?.dataset.action;
  const username = $("#adminUsername").value.trim();

  if (!username || !action) return;

  const encoded = encodeURIComponent(username);
  const endpoints = {
    giveadmin: { method: "PUT", path: `/api/admin/user/${encoded}/giveadmin` },
    deactivate: { method: "PUT", path: `/api/admin/user/${encoded}/deactivate` },
    delete: { method: "DELETE", path: `/api/admin/user/${encoded}/delete` },
  };

  const request = endpoints[action];
  const result = await apiFetch(request.path, { method: request.method });
  showStatus(result.detail || "Admin action completed.", "success");
}

function bindPageEvents(page) {
  if (page === "login") {
    $("#loginForm").addEventListener("submit", wrap(login));
    return;
  }

  if (page === "register") {
    $("#registerForm").addEventListener("submit", wrap(register));
    return;
  }

  $("#quickLogout")?.addEventListener("click", wrap(async () => {
    try {
      await apiFetch("/api/auth/logout", { method: "POST" });
    } catch {
      // Ignore server-side logout failure when clearing local session.
    }
    clearToken();
    redirectToLogin();
  }));

  if (page === "dashboard") {
    $("#refreshDashboard").addEventListener("click", wrap(loadDashboard));
  }

  if (page === "network") {
    $("#refreshPosts").addEventListener("click", wrap(async () => {
      await loadPosts();
      await renderPosts();
    }));
    $$(".filter").forEach((button) => {
      button.addEventListener("click", wrap(async () => {
        $$(".filter").forEach((item) => item.classList.remove("active"));
        button.classList.add("active");
        state.filter = button.dataset.filter;
        await renderPosts();
      }));
    });
  }

  if (page === "activity") {
    $("#reloadMine").addEventListener("click", wrap(async () => {
      await loadPosts();
      syncMyPost();
    }));
    $("#activityForm").addEventListener("submit", wrap(saveActivity));
    $("#deletePost").addEventListener("click", wrap(deleteMyPost));
    $("#activityText").addEventListener("input", updateCounter);
    $$(".category-btn").forEach((button) => {
      button.addEventListener("click", () => selectCategory(button.dataset.category));
    });
  }

  if (page === "profile") {
    $("#usernameForm").addEventListener("submit", wrap(updateUsername));
    $("#passwordForm").addEventListener("submit", wrap(updatePassword));
  }

  if (page === "admin") {
    $("#adminForm").addEventListener("submit", wrap(runAdminAction));
  }
}

async function loadPage(page) {
  if (page === "login" || page === "register") {
    if (getToken()) window.location.href = "index.html";
    return;
  }

  const user = await requireAuth();
  if (!user) return;

  if (page === "dashboard") await loadDashboard();
  if (page === "network") {
    await loadPosts();
    await renderPosts();
  }
  if (page === "activity") {
    await loadPosts();
    syncMyPost();
  }
  if (page === "admin" && !user.IsAdmin) {
    $("#adminForm").style.display = "none";
    showStatus("Admins only.", "error");
  }
}

function wrap(fn) {
  return async function wrapped(event) {
    try {
      await fn(event);
    } catch (error) {
      if (String(error.message).includes("authenticate")) {
        clearToken();
        redirectToLogin();
        return;
      }
      showStatus(error.message || "Something went wrong.", "error");
    }
  };
}

async function init() {
  const page = getPage();
  bindPageEvents(page);
  await wrap(() => loadPage(page))();
}

init();
