const $ = (sel) => document.querySelector(sel);
const state = { role: "admin", user: "demo@univ.zw" };

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

function headers() {
  const h = { "Content-Type": "application/json" };
  if (state.role) h["X-Role"] = state.role;
  h["X-User"] = state.user.trim() || "anonymous";
  return h;
}

async function api(path, { method = "GET", body } = {}) {
  const res = await fetch(path, {
    method,
    headers: headers(),
    body: body ? JSON.stringify(body) : undefined,
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    /* non-JSON response */
  }
  return { ok: res.ok, status: res.status, data };
}

function banner(id, kind, msg) {
  const el = $(id);
  el.className = "banner show " + kind;
  el.innerHTML = msg;
}
function hideBanner(id) {
  $(id).className = "banner";
}

function badge(status) {
  const cls = status === "ACTIVE" ? "active" : status === "REVOKED" ? "revoked" : "action";
  return `<span class="badge ${cls}">${esc(status)}</span>`;
}

/* ---------------- tabs ---------------- */

$("#tabs").addEventListener("click", (e) => {
  const btn = e.target.closest(".tab");
  if (!btn) return;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t === btn));
  const name = btn.dataset.tab;
  document
    .querySelectorAll(".tab-panel")
    .forEach((p) => p.classList.toggle("active", p.id === "panel-" + name));
  if (name === "search") runSearch();
  if (name === "audit") runAudit();
});

/* ---------------- identity ---------------- */

$("#role").addEventListener("change", () => {
  state.role = $("#role").value;
  refreshCurrent();
});
$("#user").addEventListener("change", () => {
  state.user = $("#user").value;
});

function refreshCurrent() {
  const active = document.querySelector(".tab-panel.active");
  if (!active) return;
  if (active.id === "panel-search") runSearch();
  if (active.id === "panel-audit") runAudit();
}

/* ---------------- verify ---------------- */

$("#verify-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideBanner("#verify-banner");
  $("#verify-result").innerHTML = "";
  const body = {
    certificate_number: $("#v-cert").value.trim(),
    holder_name: $("#v-name").value.trim(),
  };
  const r = await api("/api/v1/verify", { method: "POST", body });
  if (!r.ok) return banner("#verify-banner", "err", "Request failed (" + r.status + ").");
  renderVerify(r.data);
});

function renderVerify(d) {
  const el = $("#verify-result");
  if (d.result === "VALID") {
    el.innerHTML = `
      <div class="result-card valid show">
        <div class="result-head">✔ VALID</div>
        <table style="margin-top:10px">
          <tr><th>Holder</th><td>${esc(d.holder_name)}</td></tr>
          <tr><th>Qualification</th><td>${esc(d.qualification_name)}</td></tr>
          <tr><th>Institution</th><td>${esc(d.issuing_institution)}</td></tr>
          <tr><th>Date issued</th><td>${esc(d.date_issued)}</td></tr>
          <tr><th>Status</th><td>${badge(d.status)}</td></tr>
        </table>
      </div>`;
  } else {
    el.innerHTML = `
      <div class="result-card invalid show">
        <div class="result-head">✖ INVALID</div>
        <div class="result-reason">${esc(d.reason)}</div>
      </div>`;
  }
}

/* ---------------- demo seed ---------------- */

const DEMO_RECORDS = [
  {
    certificate_number: "ZW-ENG-2025-0001",
    holder_name: "Tendai Moyo",
    qualification_name: "BSc Computer Science",
    issuing_institution: "University of Zimbabwe",
    date_issued: "2024-06-30",
  },
  {
    certificate_number: "ZW-BUS-2024-0117",
    holder_name: "Rudo Chikafu",
    qualification_name: "BCom Accounting",
    issuing_institution: "National University of Science and Technology",
    date_issued: "2024-11-15",
  },
  {
    certificate_number: "ZW-MED-2023-0456",
    holder_name: "Farai Mutasa",
    qualification_name: "MBChB Medicine",
    issuing_institution: "University of Zimbabwe",
    date_issued: "2023-09-01",
  },
];

$("#seed-demo").addEventListener("click", async () => {
  if (!state.role) {
    return banner("#verify-banner", "info", "Switch to the <b>admin</b> role to load demo data.");
  }
  let added = 0;
  let skipped = 0;
  for (const rec of DEMO_RECORDS) {
    const r = await api("/api/v1/qualifications", { method: "POST", body: rec });
    if (r.status === 201) added++;
    else if (r.status === 409) skipped++;
  }
  banner("#verify-banner", "ok", `Demo data: ${added} registered, ${skipped} already existed.`);
});

/* ---------------- search ---------------- */

$("#search-form").addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch();
});

async function runSearch() {
  const q = $("#s-q").value.trim();
  if (!q) {
    $("#search-results").innerHTML = "";
    return;
  }
  hideBanner("#search-banner");
  const r = await api("/api/v1/qualifications?query=" + encodeURIComponent(q));
  if (r.status === 403) {
    banner("#search-banner", "info", "Search needs the <b>verifier</b> or <b>admin</b> role — use the role switcher above.");
    $("#search-results").innerHTML = "";
    return;
  }
  const rows = r.data || [];
  if (!rows.length) {
    $("#search-results").innerHTML = `<div class="empty">No records match “${esc(q)}”.</div>`;
    return;
  }
  $("#search-results").innerHTML = `
    <table style="margin-top:14px">
      <thead>
        <tr><th>Certificate</th><th>Holder</th><th>Qualification</th><th>Institution</th><th>Issued</th><th>Status</th></tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (x) => `
          <tr>
            <td>${esc(x.certificate_number)}</td>
            <td>${esc(x.holder_name)}</td>
            <td>${esc(x.qualification_name)}</td>
            <td>${esc(x.issuing_institution)}</td>
            <td>${esc(x.date_issued)}</td>
            <td>${badge(x.status)}</td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>`;
}

/* ---------------- register ---------------- */

$("#register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  hideBanner("#register-banner");
  const body = {
    certificate_number: $("#r-cert").value.trim(),
    holder_name: $("#r-name").value.trim(),
    qualification_name: $("#r-qual").value.trim(),
    issuing_institution: $("#r-inst").value.trim(),
    date_issued: $("#r-date").value,
  };
  const r = await api("/api/v1/qualifications", { method: "POST", body });
  if (r.ok) {
    banner("#register-banner", "ok", `Registered <b>${esc(r.data.certificate_number)}</b> for ${esc(r.data.holder_name)}.`);
    e.target.reset();
  } else if (r.status === 403) {
    banner("#register-banner", "info", "Registration needs the <b>admin</b> role — use the role switcher above.");
  } else if (r.status === 409) {
    banner("#register-banner", "err", esc((r.data && r.data.detail) || "Certificate already registered."));
  } else if (r.status === 422) {
    const detail = (r.data && r.data.detail) || [];
    const msg = Array.isArray(detail) ? detail.map((d) => d.msg).join("; ") : String(detail);
    banner("#register-banner", "err", "Validation failed: " + esc(msg));
  } else {
    banner("#register-banner", "err", "Request failed (" + r.status + ").");
  }
});

/* ---------------- audit ---------------- */

$("#audit-refresh").addEventListener("click", runAudit);

async function runAudit() {
  hideBanner("#audit-banner");
  const r = await api("/api/v1/audit?limit=100");
  if (r.status === 403) {
    banner("#audit-banner", "info", "The audit log is <b>admin</b> only — use the role switcher above.");
    $("#audit-results").innerHTML = "";
    return;
  }
  const rows = r.data || [];
  if (!rows.length) {
    $("#audit-results").innerHTML = `<div class="empty">No activity recorded yet.</div>`;
    return;
  }
  $("#audit-results").innerHTML = `
    <table style="margin-top:14px">
      <thead>
        <tr><th>Time</th><th>Action</th><th>Actor</th><th>Detail</th></tr>
      </thead>
      <tbody>
        ${rows
          .map(
            (x) => `
          <tr>
            <td style="white-space:nowrap">${esc(x.timestamp.replace("T", " ").slice(0, 19))}</td>
            <td><span class="badge action">${esc(x.action)}</span></td>
            <td>${esc(x.actor)}</td>
            <td>${esc(x.detail)}</td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>`;
}
