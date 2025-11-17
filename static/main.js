// main.js — Updated for enhanced Discover UI, Insights, and animations

document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("gameInput");
  const suggestionsEl = document.getElementById("suggestions");
  const gameInfoEl = document.getElementById("gameInfo");
  const recommendationsEl = document.getElementById("recommendations");
  const recommendationTitle = document.getElementById("recommendationTitle");

  let latestSuggestions = [];

  // === HELPER FUNCTIONS ===
  function hideSuggestions() {
    suggestionsEl.style.display = "none";
    suggestionsEl.innerHTML = "";
  }

  function showSuggestions(list) {
    suggestionsEl.innerHTML = "";
    if (!list || list.length === 0) {
      hideSuggestions();
      return;
    }
    list.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item.Title;
      li.dataset.id = item.id;
      li.className = "suggest-item";
      li.addEventListener("click", () => {
        input.value = item.Title;
        hideSuggestions();
        loadGameById(item.id);
      });
      suggestionsEl.appendChild(li);
    });
    suggestionsEl.style.display = "block";
  }

  // === SEARCH INPUT HANDLER ===
  let timer = null;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    const q = input.value.trim();
    if (!q) {
      hideSuggestions();
      return;
    }
    timer = setTimeout(() => {
      fetchSuggestions(q);
    }, 180);
  });

  // === ENTER TO SEARCH ===
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const q = input.value.trim();
      if (!q) return;
      const exact = latestSuggestions.find(
        (s) => s.Title.toLowerCase() === q.toLowerCase()
      );
      if (exact) {
        loadGameById(exact.id);
        hideSuggestions();
        return;
      }
      if (latestSuggestions.length > 0) {
        loadGameById(latestSuggestions[0].id);
        hideSuggestions();
        return;
      }
      fetchSuggestions(q).then(() => {
        if (latestSuggestions.length > 0) {
          loadGameById(latestSuggestions[0].id);
          hideSuggestions();
        } else {
          showNotFound();
        }
      });
    }
  });

  // === FETCH SUGGESTIONS ===
  async function fetchSuggestions(q) {
    try {
      const res = await fetch(`/api/suggest?q=${encodeURIComponent(q)}`);
      if (!res.ok) throw new Error("Suggest failed");
      const data = await res.json();
      latestSuggestions = Array.isArray(data) ? data : [];
      showSuggestions(latestSuggestions);
      return latestSuggestions;
    } catch (err) {
      console.error("Suggest error", err);
      latestSuggestions = [];
      hideSuggestions();
      return [];
    }
  }

  // === DISPLAY ERROR ===
  function showNotFound() {
    gameInfoEl.innerHTML = `<div class="card"><p style="color:var(--muted)">No game found for that query.</p></div>`;
    recommendationsEl.innerHTML = "";
    if (recommendationTitle) recommendationTitle.style.display = "none";
  }

  // === LOAD GAME BY ID ===
  async function loadGameById(id) {
    if (id === undefined || id === null) return;
    gameInfoEl.innerHTML = `<div class="card"><p>Loading game details...</p></div>`;
    recommendationsEl.innerHTML = "";
    if (recommendationTitle) recommendationTitle.style.display = "none";

    try {
      const res = await fetch(`/api/game/${encodeURIComponent(id)}`);
      const data = await res.json();
      if (!res.ok || data.error) {
        console.error("Game fetch error", data);
        showNotFound();
        return;
      }
      renderGame(data);
    } catch (err) {
      console.error("Fetch game failed", err);
      showNotFound();
    }
  }

  // === RENDER GAME INFO ===
  function renderGame(data) {
    const title = data.Title || data.title || "Untitled";
    const desc = data["Game Description"] || data.description || "";
    const dev = data.Developer || "";
    const pub = data.Publisher || "";
    const year = data["Release Date"] || "";
    const tagsRaw = data["Popular Tags"] || "";
    const tags = String(tagsRaw)
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean);
    const link = data.Link || "#";
    const langs = data["Supported Languages"] || "";

    const tagHtml = tags
      .slice(0, 6)
      .map((t) => `<span class="badge">${t}</span>`)
      .join(" ");

    // ✅ Game Info Card with "View Insights"
    gameInfoEl.innerHTML = `
      <div class="card game-card">
        <h3>${escapeHtml(title)}</h3>
        <div class="meta">By ${escapeHtml(dev)} ${year ? " • " + escapeHtml(year) : ""}</div>
        <div style="margin:10px 0">${tagHtml}</div>
        <p style="line-height:1.4;color:#dbeaf5">${escapeHtml(desc).slice(0, 1000)}</p>
        <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
          <a target="_blank" href="${escapeAttr(link)}" class="login-btn" 
            style="padding:8px 12px;font-size:14px;border-radius:8px;">
            Open on Steam
          </a>
          <a href="/insights/${data.id}" class="login-btn"
            style="padding:8px 12px;font-size:14px;border-radius:8px;background:linear-gradient(90deg,#00b4d8,#be00ff);">
            View Insights
          </a>
        </div>
      </div>
    `;

    // ✅ Recommendations
    const recs = data.recommendations || [];
    recommendationsEl.innerHTML = "";
    if (recs.length > 0) {
      if (recommendationTitle) recommendationTitle.style.display = "block";
      recs.forEach((r) => {
        const card = document.createElement("div");
        card.className = "card";
        const rtags = (r["Popular Tags"] || "")
          .split(",")
          .slice(0, 3)
          .map((t) => `<span class="badge">${escapeHtml(t.trim())}</span>`)
          .join(" ");
        card.innerHTML = `
          <h4 style="margin:0 0 6px 0">${escapeHtml(r.Title || "Untitled")}</h4>
          <div class="meta">${escapeHtml(r.Developer || "")}</div>
          <div style="margin-top:8px">${rtags}</div>
          <div style="margin-top:10px;display:flex;gap:8px;">
            <a class="login-btn" target="_blank" href="${escapeAttr(r.Link || '#')}"
              style="padding:8px 10px;font-size:13px;border-radius:8px;">Steam</a>
            <a class="login-btn" href="/insights/${r.id}"
              style="padding:8px 10px;font-size:13px;border-radius:8px;background:linear-gradient(90deg,#00b4d8,#be00ff);">
              Insights
            </a>
          </div>
        `;
        if (r.id !== undefined && r.id !== null) {
          card.style.cursor = "pointer";
          card.addEventListener("click", () => loadGameById(r.id));
        }
        recommendationsEl.appendChild(card);
      });
    } else {
      recommendationsEl.innerHTML =
        "<div class='card'><p style='color:var(--muted)'>No recommendations available.</p></div>";
      if (recommendationTitle) recommendationTitle.style.display = "none";
    }
  }

  // === Escape Helpers ===
  function escapeHtml(s) {
    if (!s) return "";
    return String(s)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }
  function escapeAttr(s) {
    if (!s) return "#";
    return String(s).replaceAll('"', "&quot;").replaceAll("'", "&#39;");
  }

  // === HIDE SUGGESTIONS WHEN CLICKING OUTSIDE ===
  document.addEventListener("click", (e) => {
    if (!suggestionsEl.contains(e.target) && e.target !== input) hideSuggestions();
  });

  // === Optional: Interactive Shape Motion (parallax-like) ===
  const shapes = document.querySelectorAll(".shape");
  if (shapes.length > 0) {
    document.addEventListener("mousemove", (e) => {
      const x = (e.clientX / window.innerWidth - 0.5) * 2;
      const y = (e.clientY / window.innerHeight - 0.5) * 2;
      shapes.forEach((shape, i) => {
        const speed = (i + 1) * 0.8;
        shape.style.transform = `translate(${x * speed * 10}px, ${y * speed * 10}px) rotate(${x * y * 30}deg)`;
      });
    });
  }

  // Auto focus input
  try { input.focus(); } catch (e) {}
});
