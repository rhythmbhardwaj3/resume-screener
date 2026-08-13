// ============================================================
// State
// ============================================================
let jdMode = "paste";       // "paste" | "file"
let jdFile = null;
let resumeFiles = [];       // array of File objects
let lastResults = null;     // cached for CSV export

// ============================================================
// Elements
// ============================================================
const jdTextarea   = document.getElementById("jdText");
const jdDropzone    = document.getElementById("jdDropzone");
const jdFileInput   = document.getElementById("jdFileInput");
const jdFileNameEl  = document.getElementById("jdFileName");
const toggleBtns    = document.querySelectorAll(".toggle-btn");

const resumeDropzone  = document.getElementById("resumeDropzone");
const resumeFileInput = document.getElementById("resumeFileInput");
const resumeListEl    = document.getElementById("resumeList");

const skillW  = document.getElementById("skillW");
const keywordW = document.getElementById("keywordW");
const expW    = document.getElementById("expW");
const skillWVal  = document.getElementById("skillWVal");
const keywordWVal = document.getElementById("keywordWVal");
const expWVal    = document.getElementById("expWVal");

const screenBtn      = document.getElementById("screenBtn");
const errorMsg        = document.getElementById("errorMsg");
const resultsSection  = document.getElementById("resultsSection");
const resultsList     = document.getElementById("resultsList");
const loadingOverlay  = document.getElementById("loadingOverlay");
const downloadCsvBtn  = document.getElementById("downloadCsv");

const SUPPORTED_EXT = [".pdf", ".docx", ".txt"];

// ============================================================
// JD input mode toggle
// ============================================================
toggleBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    toggleBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    jdMode = btn.dataset.mode;
    jdTextarea.classList.toggle("hidden", jdMode !== "paste");
    jdDropzone.classList.toggle("hidden", jdMode !== "file");
  });
});

// ============================================================
// JD file dropzone
// ============================================================
jdDropzone.addEventListener("click", () => jdFileInput.click());
jdDropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") jdFileInput.click();
});
jdFileInput.addEventListener("change", (e) => {
  if (e.target.files.length) setJdFile(e.target.files[0]);
});
setupDragEvents(jdDropzone, (files) => {
  if (files.length) setJdFile(files[0]);
});

function setJdFile(file) {
  const ext = "." + file.name.split(".").pop().toLowerCase();
  if (!SUPPORTED_EXT.includes(ext)) {
    showError(`Unsupported file type: ${ext}`);
    return;
  }
  jdFile = file;
  jdFileNameEl.textContent = "";
  const label = document.createElement("span");
  label.textContent = "📄 " + file.name;
  const removeBtn = document.createElement("button");
  removeBtn.textContent = "remove";
  removeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    jdFile = null;
    jdFileNameEl.classList.add("hidden");
    jdFileInput.value = "";
  });
  jdFileNameEl.appendChild(label);
  jdFileNameEl.appendChild(removeBtn);
  jdFileNameEl.classList.remove("hidden");
}

// ============================================================
// Resume dropzone (multi-file)
// ============================================================
resumeDropzone.addEventListener("click", () => resumeFileInput.click());
resumeDropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") resumeFileInput.click();
});
resumeFileInput.addEventListener("change", (e) => {
  addResumeFiles(Array.from(e.target.files));
  resumeFileInput.value = "";
});
setupDragEvents(resumeDropzone, (files) => addResumeFiles(files));

function addResumeFiles(files) {
  for (const file of files) {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!SUPPORTED_EXT.includes(ext)) {
      showError(`Skipped "${file.name}" — unsupported file type.`);
      continue;
    }
    // avoid exact duplicate name+size
    if (resumeFiles.some(f => f.name === file.name && f.size === file.size)) continue;
    resumeFiles.push(file);
  }
  renderResumeList();
}

function renderResumeList() {
  resumeListEl.innerHTML = "";
  resumeFiles.forEach((file, idx) => {
    const li = document.createElement("li");
    const nameSpan = document.createElement("span");
    nameSpan.className = "fname";
    nameSpan.textContent = "📋 " + file.name;
    const removeBtn = document.createElement("button");
    removeBtn.textContent = "✕";
    removeBtn.title = "Remove";
    removeBtn.addEventListener("click", () => {
      resumeFiles.splice(idx, 1);
      renderResumeList();
    });
    li.appendChild(nameSpan);
    li.appendChild(removeBtn);
    resumeListEl.appendChild(li);
  });
}

function setupDragEvents(el, onDrop) {
  ["dragenter", "dragover"].forEach(evt =>
    el.addEventListener(evt, (e) => {
      e.preventDefault();
      el.classList.add("dragover");
    })
  );
  ["dragleave", "drop"].forEach(evt =>
    el.addEventListener(evt, (e) => {
      e.preventDefault();
      el.classList.remove("dragover");
    })
  );
  el.addEventListener("drop", (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files || []);
    onDrop(files);
  });
}

// ============================================================
// Weight sliders
// ============================================================
function updateWeightLabels() {
  skillWVal.textContent = skillW.value + "%";
  keywordWVal.textContent = keywordW.value + "%";
  expWVal.textContent = expW.value + "%";
}
[skillW, keywordW, expW].forEach(s => s.addEventListener("input", updateWeightLabels));
updateWeightLabels();

// ============================================================
// Submit
// ============================================================
screenBtn.addEventListener("click", async () => {
  hideError();

  const hasJd = (jdMode === "paste" && jdTextarea.value.trim()) || (jdMode === "file" && jdFile);
  if (!hasJd) {
    showError("Please provide a job description (paste text or upload a file).");
    return;
  }
  if (resumeFiles.length === 0) {
    showError("Please add at least one resume.");
    return;
  }

  const formData = new FormData();
  if (jdMode === "paste") {
    formData.append("jd_text", jdTextarea.value.trim());
  } else {
    formData.append("jd_file", jdFile);
  }
  resumeFiles.forEach(f => formData.append("resume_files", f));
  formData.append("skill_weight", skillW.value);
  formData.append("keyword_weight", keywordW.value);
  formData.append("experience_weight", expW.value);

  loadingOverlay.classList.remove("hidden");
  resultsSection.classList.add("hidden");

  try {
    const res = await fetch("/api/rank", { method: "POST", body: formData });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || "Something went wrong while screening candidates.");
      return;
    }

    if (data.skipped && data.skipped.length) {
      showError(`Note: skipped ${data.skipped.length} file(s) that couldn't be parsed: ${data.skipped.join(", ")}`);
    }

    lastResults = data.results;
    renderResults(data.results);
  } catch (err) {
    showError("Could not reach the server. Is server.py running?");
  } finally {
    loadingOverlay.classList.add("hidden");
  }
});

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove("hidden");
}
function hideError() {
  errorMsg.classList.add("hidden");
  errorMsg.textContent = "";
}

// ============================================================
// Render results
// ============================================================
function gradeFor(score) {
  if (score >= 75) return { label: "STRONG MATCH", cls: "strong" };
  if (score >= 50) return { label: "REVIEW", cls: "review" };
  return { label: "WEAK MATCH", cls: "weak" };
}

function renderResults(results) {
  resultsList.innerHTML = "";
  results.forEach((r, i) => {
    const grade = gradeFor(r.overall_score);

    const card = document.createElement("div");
    card.className = "case-card";
    card.style.animationDelay = `${i * 0.05}s`;

    card.innerHTML = `
      <div class="case-card-top">
        <div>
          <div class="case-rank">CANDIDATE ${String(r.rank).padStart(2, "0")}</div>
          <p class="case-name">${escapeHtml(r.resume_name)}</p>
          <span class="stamp ${grade.cls}">${grade.label}</span>
        </div>
        <div class="case-score">${r.overall_score}<span> / 100</span></div>
      </div>

      <div class="meters">
        ${meterHtml("Skill match", r.skill_score)}
        ${meterHtml("Keyword match", r.keyword_score)}
        ${meterHtml("Experience", r.experience_score)}
      </div>

      <div class="tag-group">
        <span class="tag-group-label">Matched skills (${r.matched_skills.length})</span>
        <div class="tags">
          ${r.matched_skills.length ? r.matched_skills.map(s => `<span class="tag matched">${escapeHtml(s)}</span>`).join("") : '<span class="tag matched" style="opacity:.5">none found</span>'}
        </div>
      </div>

      <div class="tag-group">
        <span class="tag-group-label">Missing skills (${r.missing_skills.length})</span>
        <div class="tags">
          ${r.missing_skills.length ? r.missing_skills.map(s => `<span class="tag missing">${escapeHtml(s)}</span>`).join("") : '<span class="tag matched" style="opacity:.5">none — full coverage</span>'}
        </div>
      </div>

      <div class="exp-line">
        Years on file: ${r.resume_years || "not stated"} &nbsp;|&nbsp; JD requires: ${r.jd_years_required || "not specified"}
      </div>
    `;
    resultsList.appendChild(card);
  });

  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function meterHtml(label, value) {
  return `
    <div class="meter">
      <label>${label}</label>
      <div class="meter-track"><div class="meter-fill" style="width:${Math.min(value, 100)}%"></div></div>
      <div class="meter-value">${value}%</div>
    </div>
  `;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ============================================================
// CSV export
// ============================================================
downloadCsvBtn.addEventListener("click", () => {
  if (!lastResults) return;
  const headers = ["Rank", "Resume", "Overall Score", "Skill Match %", "Keyword Match %", "Experience Match %", "Years Found", "JD Years Required", "Matched Skills", "Missing Skills"];
  const rows = lastResults.map(r => [
    r.rank, r.resume_name, r.overall_score, r.skill_score, r.keyword_score, r.experience_score,
    r.resume_years, r.jd_years_required, r.matched_skills.join("; "), r.missing_skills.join("; ")
  ]);
  const csv = [headers, ...rows]
    .map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(","))
    .join("\n");

  const blob = new Blob([csv], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "resume_ranking_report.csv";
  a.click();
  URL.revokeObjectURL(url);
});
