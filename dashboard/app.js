/**
 * JARVIS Control Center & Engine Configurator App Logic.
 */

let allEngines = [];
let currentCoreConfig = {};
let activeModalEngine = null;

// Tab Switching
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));

  const targetTab = document.getElementById(tabId);
  if (targetTab) targetTab.classList.add('active');

  const navBtn = document.getElementById('nav-' + tabId.replace('tab-', ''));
  if (navBtn) navBtn.classList.add('active');

  if (tabId === 'tab-engines') loadEngines();
  if (tabId === 'tab-security') loadSecurityMatrix();
  if (tabId === 'tab-core') loadCoreConfig();
}

// Fetch System Status & Telemetry
async function loadStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();

    document.getElementById('activeEnginesCount').innerText = `${data.active_engines} Engines Active`;
    document.getElementById('kpiEngines').innerText = `${data.active_engines} / 17`;
    document.getElementById('kpiCapabilities').innerText = data.total_capabilities || 68;

    fetchTelemetry();
    runAllHealthChecks();
  } catch (err) {
    console.error("Failed to fetch status:", err);
  }
}

// Fetch All Engines (17 Engines Manifest)
async function loadEngines() {
  const container = document.getElementById('enginesContainer');
  container.innerHTML = '<div class="loading-spinner">Loading engine plugins...</div>';

  try {
    const res = await fetch('/api/engines');
    allEngines = await res.json();

    document.getElementById('enginesBadge').innerText = allEngines.length;
    renderEngines(allEngines);
  } catch (err) {
    container.innerHTML = '<div class="error-msg">Failed to load engine plugins.</div>';
    console.error("Failed to load engines:", err);
  }
}

// Render Engines Cards Grid
function renderEngines(engines) {
  const container = document.getElementById('enginesContainer');
  container.innerHTML = '';

  engines.forEach(eng => {
    const card = document.createElement('div');
    card.className = 'engine-card';
    card.onclick = () => openEngineModal(eng);

    const capTags = eng.capabilities.map(c => `<span class="cap-tag">${c.name} (${c.risk_level})</span>`).join('');

    card.innerHTML = `
      <div>
        <div class="engine-card-header">
          <div class="engine-title-group">
            <h4>${eng.name}</h4>
            <span class="engine-id">id: ${eng.engine_id}</span>
          </div>
          <span class="badge-risk risk-normal">Active</span>
        </div>
        <p class="engine-desc">${eng.description}</p>
        <div class="caps-tags">${capTags}</div>
      </div>
      <div class="engine-card-footer">
        <span class="status-text" style="color: var(--primary-green); font-size:12px;">● Health: OK</span>
        <button class="btn btn-sm btn-secondary" onclick="event.stopPropagation(); openEngineModalById('${eng.engine_id}')">Configure</button>
      </div>
    `;

    container.appendChild(card);
  });
}

// Filter Engines
function filterEngines() {
  const q = document.getElementById('searchEnginesInput').value.toLowerCase();
  const filtered = allEngines.filter(e => e.name.toLowerCase().includes(q) || e.engine_id.toLowerCase().includes(q) || e.description.toLowerCase().includes(q));
  renderEngines(filtered);
}

// Open Engine Config Modal
function openEngineModal(eng) {
  activeModalEngine = eng;
  document.getElementById('modalEngineTitle').innerText = `Configure ${eng.name} (${eng.engine_id})`;

  const modalBody = document.getElementById('modalEngineBody');
  let capRows = eng.capabilities.map(c => `
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; padding:10px; background:rgba(0,0,0,0.2); border-radius:6px;">
      <div>
        <strong style="font-size:13px; color:var(--primary-cyan);">${c.name}</strong>
      </div>
      <select onchange="updateCapabilityRisk('${c.name}', this.value)" style="width:140px;">
        <option value="NORMAL" ${c.risk_level === 'NORMAL' ? 'selected' : ''}>NORMAL</option>
        <option value="SENSITIVE" ${c.risk_level === 'SENSITIVE' ? 'selected' : ''}>SENSITIVE</option>
        <option value="CRITICAL" ${c.risk_level === 'CRITICAL' ? 'selected' : ''}>CRITICAL</option>
      </select>
    </div>
  `).join('');

  modalBody.innerHTML = `
    <p style="color:var(--text-muted); font-size:13px; margin-bottom:16px;">${eng.description}</p>
    <h4 style="margin-bottom:12px; font-size:14px;">Capability Risk Permissions</h4>
    <div>${capRows}</div>
  `;

  document.getElementById('engineModal').classList.add('active');
}

function openEngineModalById(engineId) {
  const eng = allEngines.find(e => e.engine_id === engineId);
  if (eng) openEngineModal(eng);
}

function closeModal() {
  document.getElementById('engineModal').classList.remove('active');
  activeModalEngine = null;
}

// Update Risk Level Endpoint
async function updateCapabilityRisk(capName, riskLevel) {
  try {
    const res = await fetch('/api/engines/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ capability: capName, risk_level: riskLevel })
    });
    const data = await res.json();
    showToast(`Updated risk level for '${capName}' to ${riskLevel}`);
  } catch (err) {
    showToast(`Failed to update capability risk`, true);
  }
}

// Save Engine Modal Changes
function saveEngineModalConfig() {
  closeModal();
  loadEngines();
}

// Load Security Risk Table
async function loadSecurityMatrix() {
  if (!allEngines || allEngines.length === 0) {
    await loadEngines();
  }
  const tbody = document.getElementById('securityTableBody');
  tbody.innerHTML = '';

  allEngines.forEach(eng => {
    eng.capabilities.forEach(cap => {
      const tr = document.createElement('tr');
      const riskClass = cap.risk_level === 'CRITICAL' ? 'risk-critical' : (cap.risk_level === 'SENSITIVE' ? 'risk-sensitive' : 'risk-normal');
      tr.innerHTML = `
        <td><code style="color:var(--primary-cyan);">${cap.name}</code></td>
        <td>${eng.name} (${eng.engine_id})</td>
        <td><span class="badge-risk ${riskClass}">${cap.risk_level}</span></td>
        <td>
          <select onchange="updateCapabilityRisk('${cap.name}', this.value)" style="width:130px; padding:4px 8px; font-size:12px;">
            <option value="NORMAL" ${cap.risk_level === 'NORMAL' ? 'selected' : ''}>NORMAL</option>
            <option value="SENSITIVE" ${cap.risk_level === 'SENSITIVE' ? 'selected' : ''}>SENSITIVE</option>
            <option value="CRITICAL" ${cap.risk_level === 'CRITICAL' ? 'selected' : ''}>CRITICAL</option>
          </select>
        </td>
      `;
      tbody.appendChild(tr);
    });
  });
}

// Load Core Config & Applications
async function loadCoreConfig() {
  try {
    const res = await fetch('/api/core/config');
    currentCoreConfig = await res.json();

    const appForm = document.getElementById('appPathsForm');
    appForm.innerHTML = '';

    const apps = currentCoreConfig.applications || {};
    Object.keys(apps).forEach(appKey => {
      const field = document.createElement('div');
      field.style.marginBottom = '12px';
      field.innerHTML = `
        <label style="display:block; font-size:12px; color:var(--text-muted); margin-bottom:4px;">${appKey}</label>
        <input type="text" id="cfg_app_${appKey}" value="${apps[appKey]}">
      `;
      appForm.appendChild(field);
    });

    const voiceForm = document.getElementById('voiceSettingsForm');
    voiceForm.innerHTML = '';
    const voice = currentCoreConfig.voice || {};
    Object.keys(voice).forEach(vKey => {
      const field = document.createElement('div');
      field.style.marginBottom = '12px';
      field.innerHTML = `
        <label style="display:block; font-size:12px; color:var(--text-muted); margin-bottom:4px;">${vKey}</label>
        <input type="text" id="cfg_voice_${vKey}" value="${voice[vKey]}">
      `;
      voiceForm.appendChild(field);
    });
  } catch (err) {
    console.error("Failed to load core config:", err);
  }
}

async function saveCoreConfig() {
  try {
    const apps = currentCoreConfig.applications || {};
    Object.keys(apps).forEach(appKey => {
      const input = document.getElementById(`cfg_app_${appKey}`);
      if (input) apps[appKey] = input.value;
    });

    const voice = currentCoreConfig.voice || {};
    Object.keys(voice).forEach(vKey => {
      const input = document.getElementById(`cfg_voice_${vKey}`);
      if (input) voice[vKey] = input.value;
    });

    const res = await fetch('/api/core/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ applications: apps, voice: voice })
    });
    showToast("Core configuration saved successfully.");
  } catch (err) {
    showToast("Failed to save core configuration.", true);
  }
}

// Telemetry & Health Checks
async function fetchTelemetry() {
  try {
    const res = await fetch('/api/telemetry');
    const logs = await res.json();
    const feed = document.getElementById('telemetryFeed');
    feed.innerHTML = '';

    logs.forEach(log => {
      const item = document.createElement('div');
      item.className = 'feed-item';
      item.innerHTML = `<span class="time">[${log.role.toUpperCase()}]</span> <span class="msg">${log.content}</span>`;
      feed.appendChild(item);
    });
  } catch (err) {
    console.error(err);
  }
}

async function runAllHealthChecks() {
  try {
    const res = await fetch('/api/engines/health', { method: 'POST' });
    const healthMap = await res.json();
    const list = document.getElementById('quickHealthList');
    list.innerHTML = '';

    Object.keys(healthMap).forEach(engId => {
      const h = healthMap[engId];
      const item = document.createElement('div');
      item.className = 'health-item';
      item.innerHTML = `
        <span class="health-name">${engId}</span>
        <span class="health-status-ok">● ${h.status || 'ok'}</span>
      `;
      list.appendChild(item);
    });
  } catch (err) {
    console.error(err);
  }
}

// Live Prompt Test Execution
async function runPromptTest() {
  const input = document.getElementById('txtPromptInput');
  const prompt = input.value.strip ? input.value.strip() : input.value.trim();
  if (!prompt) return;

  const consoleOutput = document.getElementById('consoleOutput');

  // User log entry
  const userEntry = document.createElement('div');
  userEntry.className = 'log-entry user';
  userEntry.innerText = `[USER]: ${prompt}`;
  consoleOutput.appendChild(userEntry);

  input.value = '';
  consoleOutput.scrollTop = consoleOutput.scrollHeight;

  try {
    const res = await fetch('/api/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const data = await res.json();

    const jarvisEntry = document.createElement('div');
    jarvisEntry.className = 'log-entry jarvis';
    jarvisEntry.innerText = `[JARVIS]: ${data.output}`;
    consoleOutput.appendChild(jarvisEntry);

    consoleOutput.scrollTop = consoleOutput.scrollHeight;
  } catch (err) {
    const errEntry = document.createElement('div');
    errEntry.className = 'log-entry sys';
    errEntry.innerText = `[ERROR]: ${err.message}`;
    consoleOutput.appendChild(errEntry);
  }
}

function clearConsoleLog() {
  document.getElementById('consoleOutput').innerHTML = '';
}

// Toast Notifications
function showToast(msg, isError = false) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = 'toast';
  if (isError) toast.style.borderColor = 'var(--primary-red)';
  toast.innerText = msg;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3500);
}

// ============================================================
// HUMAN LANGUAGE TO MACHINE LANGUAGE AI MODEL CONTROLLER
// ============================================================

let currentMachineCommand = null;
let currentCodeTab = 'json';
let speechRecognitionInstance = null;
let isRecordingVoice = false;

function loadNLUPreset(text) {
  const input = document.getElementById('txtHumanInput');
  input.value = text;
  interpretHumanInput();
}

function clearNLUInput() {
  document.getElementById('txtHumanInput').value = '';
  document.getElementById('voiceReviewHint').style.display = 'none';
  document.getElementById('nluTelemetryStrip').style.display = 'none';
  document.getElementById('nluComparisonGrid').style.display = 'none';
  document.getElementById('clarificationAlert').style.display = 'none';
  document.getElementById('execResultBox').style.display = 'none';
  currentMachineCommand = null;
}

function toggleVoiceRecording() {
  if (isRecordingVoice) {
    stopVoiceRecording();
  } else {
    startVoiceRecording();
  }
}

function startVoiceRecording() {
  const selectedLang = document.getElementById('nluLangSelect').value;
  const langMap = {
    'auto': 'en-IN',
    'en': 'en-IN',
    'hi': 'hi-IN',
    'mr': 'mr-IN',
    'hinglish': 'hi-IN'
  };
  const targetSpeechLang = langMap[selectedLang] || 'en-IN';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecognition) {
    try {
      speechRecognitionInstance = new SpeechRecognition();
      speechRecognitionInstance.lang = targetSpeechLang;
      speechRecognitionInstance.interimResults = true;
      speechRecognitionInstance.continuous = false;

      updateVoiceUIState(true, `Listening (${targetSpeechLang})...`);

      speechRecognitionInstance.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          transcript += event.results[i][0].transcript;
        }
        document.getElementById('txtHumanInput').value = transcript;
        document.getElementById('voiceReviewHint').style.display = 'flex';
      };

      speechRecognitionInstance.onerror = (event) => {
        console.warn('Web Speech error:', event.error);
        stopVoiceRecording();
        showToast(`Voice capture notice: ${event.error}. Falling back to backend microphone...`, false);
        fallbackBackendVoiceListen(selectedLang);
      };

      speechRecognitionInstance.onend = () => {
        stopVoiceRecording();
        showToast('Speech recorded. Review transcript or click Interpret.', false);
      };

      speechRecognitionInstance.start();
      isRecordingVoice = true;
      return;
    } catch (err) {
      console.warn('SpeechRecognition failed to start:', err);
    }
  }

  // Fallback to backend python microphone if browser speech is unavailable
  fallbackBackendVoiceListen(selectedLang);
}

function stopVoiceRecording() {
  if (speechRecognitionInstance) {
    try { speechRecognitionInstance.stop(); } catch (e) {}
  }
  isRecordingVoice = false;
  updateVoiceUIState(false, 'Microphone Idle');
}

function updateVoiceUIState(recording, text) {
  const micBtn = document.getElementById('btnMicRecord');
  const pill = document.getElementById('voiceStatusPill');
  const wave = document.getElementById('micWaveform');
  const label = document.getElementById('voiceStatusText');

  label.innerText = text;

  if (recording) {
    micBtn.classList.add('recording');
    pill.classList.add('recording');
    wave.style.display = 'flex';
  } else {
    micBtn.classList.remove('recording');
    pill.classList.remove('recording');
    wave.style.display = 'none';
  }
}

async function fallbackBackendVoiceListen(lang) {
  updateVoiceUIState(true, `Calibrating Mic (${lang})...`);
  try {
    const res = await fetch('/api/nlu/voice-listen', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: lang, timeout: 5 })
    });
    const data = await res.json();
    stopVoiceRecording();

    if (data.success && data.transcript) {
      document.getElementById('txtHumanInput').value = data.transcript;
      document.getElementById('voiceReviewHint').style.display = 'flex';
      showToast(`Voice recognized: "${data.transcript}"`);
    } else {
      showToast(data.error || 'No speech detected.', true);
    }
  } catch (err) {
    stopVoiceRecording();
    showToast(`Microphone service error: ${err.message}`, true);
  }
}

async function interpretHumanInput() {
  const query = document.getElementById('txtHumanInput').value.trim();
  if (!query) {
    showToast('Please type or speak a command first.', true);
    return;
  }

  showToast('Interpreting human communication...', false);

  try {
    const res = await fetch('/api/nlu/interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });
    const data = await res.json();
    const cmd = data.command;
    const val = data.validation;

    currentMachineCommand = cmd;
    renderNLUResults(cmd, val);
  } catch (err) {
    showToast(`Interpretation failed: ${err.message}`, true);
  }
}

function renderNLUResults(cmd, val) {
  // 1. Reveal Telemetry & Comparison Grid
  document.getElementById('nluTelemetryStrip').style.display = 'flex';
  document.getElementById('nluComparisonGrid').style.display = 'grid';
  document.getElementById('execResultBox').style.display = 'none';

  // 2. Populate Telemetry Strip
  const langNames = { en: 'English', hi: 'Hindi', mr: 'Marathi', hinglish: 'Hinglish' };
  document.getElementById('telemetryLang').innerText = langNames[cmd.detected_language] || cmd.detected_language;
  document.getElementById('telemetryIntent').innerText = cmd.intent;
  document.getElementById('telemetryEngine').innerText = cmd.engine.toUpperCase();
  document.getElementById('telemetryConf').innerText = `${Math.round(cmd.confidence * 100)}%`;

  const validBadge = document.getElementById('telemetryValidation');
  if (val.is_valid) {
    validBadge.innerText = '✅ Valid Schema';
    validBadge.style.color = '#4ade80';
    validBadge.style.background = 'rgba(34, 197, 94, 0.15)';
  } else {
    validBadge.innerText = '❌ Schema Error';
    validBadge.style.color = '#ef4444';
    validBadge.style.background = 'rgba(239, 68, 68, 0.15)';
  }

  const riskBadge = document.getElementById('telemetryRisk');
  riskBadge.className = `t-val badge-risk ${cmd.risk_level}`;
  riskBadge.innerText = cmd.risk_level;

  // 3. Populate Left Panel (Human Communication Analysis)
  document.getElementById('humanLangBadge').innerText = cmd.detected_language.toUpperCase();
  document.getElementById('analysisRaw').innerText = `"${cmd.raw_input}"`;
  document.getElementById('analysisNormalized').innerText = `"${cmd.normalized_input}"`;
  document.getElementById('analysisExplanation').innerText = cmd.explanation;

  const entitiesTbody = document.getElementById('analysisEntitiesBody');
  entitiesTbody.innerHTML = '';
  const paramEntries = Object.entries(cmd.parameters);

  if (paramEntries.length === 0) {
    entitiesTbody.innerHTML = '<tr><td colspan="3" style="color: var(--text-muted); text-align: center;">No specific parameters required</td></tr>';
  } else {
    paramEntries.forEach(([key, val]) => {
      const tr = document.createElement('tr');
      const valDisplay = typeof val === 'object' ? JSON.stringify(val) : String(val);
      tr.innerHTML = `<td><strong>${key}</strong></td><td>${valDisplay}</td><td><span class="badge">${typeof val}</span></td>`;
      entitiesTbody.appendChild(tr);
    });
  }

  // 4. Ambiguity / Clarification Alert Check
  const clarAlert = document.getElementById('clarificationAlert');
  if (cmd.ambiguity_detected) {
    clarAlert.style.display = 'flex';
    document.getElementById('clarificationQuestionText').innerText = cmd.clarification_question || 'Ambiguity detected.';

    const optDiv = document.getElementById('clarificationOptions');
    optDiv.innerHTML = '';

    if (cmd.intent.includes('delete')) {
      ['Project Alpha', 'Project Orion v1', 'Cancel Action'].forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'preset-chip';
        btn.innerText = opt;
        btn.onclick = () => {
          if (opt === 'Cancel Action') {
            clarAlert.style.display = 'none';
          } else {
            document.getElementById('txtHumanInput').value = `Delete folder "${opt}"`;
            interpretHumanInput();
          }
        };
        optDiv.appendChild(btn);
      });
    } else if (cmd.intent.includes('clean')) {
      ['Clean Temp Files', 'Empty Recycle Bin', 'Optimize RAM'].forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'preset-chip';
        btn.innerText = opt;
        btn.onclick = () => {
          document.getElementById('txtHumanInput').value = opt;
          interpretHumanInput();
        };
        optDiv.appendChild(btn);
      });
    }
  } else {
    clarAlert.style.display = 'none';
  }

  // 5. Populate Right Panel (Code Outputs)
  switchCodeTab(currentCodeTab);

  // Security Note
  const secNote = document.getElementById('execSecurityNote');
  secNote.innerText = cmd.safety_notes || (cmd.requires_confirmation ? '⚠️ Requires explicit user confirmation.' : 'Security: Verified allowlisted action.');
  if (cmd.requires_confirmation) {
    secNote.style.color = '#f59e0b';
  } else {
    secNote.style.color = 'var(--text-muted)';
  }
}

function switchCodeTab(tab) {
  currentCodeTab = tab;
  document.querySelectorAll('.code-tab').forEach(b => b.classList.remove('active'));

  const matchingBtn = Array.from(document.querySelectorAll('.code-tab')).find(b => b.innerText.toLowerCase().includes(tab));
  if (matchingBtn) matchingBtn.classList.add('active');

  const viewer = document.getElementById('codeOutputViewer');
  if (!currentMachineCommand || !currentMachineCommand.generated_code) {
    viewer.innerText = '// No code generated yet';
    return;
  }

  const codeObj = currentMachineCommand.generated_code;
  if (tab === 'json') {
    viewer.innerText = codeObj.json_cmd || JSON.stringify(currentMachineCommand, null, 2);
  } else if (tab === 'python') {
    viewer.innerText = codeObj.python || '# Python execution code not applicable';
  } else if (tab === 'javascript') {
    viewer.innerText = codeObj.javascript || '// JavaScript execution code not applicable';
  } else if (tab === 'sql') {
    viewer.innerText = codeObj.sql || '-- SQL schema query not applicable';
  } else if (tab === 'shell') {
    viewer.innerText = codeObj.shell || '# Shell script not applicable';
  }
}

function copyCurrentCode() {
  const viewer = document.getElementById('codeOutputViewer');
  if (!viewer || !viewer.innerText) return;
  navigator.clipboard.writeText(viewer.innerText).then(() => {
    showToast('Code copied to clipboard! 📋');
  });
}

async function executeCurrentMachineCommand() {
  if (!currentMachineCommand) {
    showToast('No active command to execute.', true);
    return;
  }

  if (currentMachineCommand.ambiguity_detected) {
    showToast('Cannot execute ambiguous command. Please answer clarification first.', true);
    return;
  }

  let confirmed = true;
  if (currentMachineCommand.requires_confirmation || currentMachineCommand.risk_level === 'CRITICAL') {
    confirmed = confirm(`[SECURITY WARNING]: Action '${currentMachineCommand.action}' is marked as ${currentMachineCommand.risk_level}.\n\n${currentMachineCommand.safety_notes}\n\nDo you authorize execution on your PC?`);
    if (!confirmed) {
      showToast('Execution cancelled by user.', true);
      return;
    }
  }

  showToast('Executing command via Orion Execution Adapter...', false);

  try {
    const res = await fetch('/api/nlu/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        command: currentMachineCommand,
        confirmed: confirmed
      })
    });
    const result = await res.json();

    const resultBox = document.getElementById('execResultBox');
    const statusBadge = document.getElementById('execResultStatus');
    const msgSpan = document.getElementById('execResultMessage');

    resultBox.style.display = 'flex';
    if (result.success) {
      statusBadge.innerText = 'EXECUTED';
      statusBadge.style.background = '#22c55e';
      msgSpan.innerText = result.message || 'Action executed successfully.';
      showToast('Command executed successfully! 🚀');
    } else {
      statusBadge.innerText = 'FAILED';
      statusBadge.style.background = '#ef4444';
      msgSpan.innerText = result.message || result.error || 'Execution blocked.';
      showToast(`Execution blocked: ${result.message}`, true);
    }
  } catch (err) {
    showToast(`Execution request failed: ${err.message}`, true);
  }
}

async function retrainNLUModel() {
  showToast('Retraining Orion NLU Model on latest capability matrix...', false);
  try {
    const res = await fetch('/api/nlu/train', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
      const acc = Math.round(data.metadata.training_accuracy * 100);
      document.getElementById('nluModelStatus').innerText = `Trained Orion Model: ${acc}% Acc`;
      showToast(`Model retrained successfully with ${acc}% accuracy! 🎯`);
    } else {
      showToast('Model training completed with warnings.', true);
    }
  } catch (err) {
    showToast(`Training error: ${err.message}`, true);
  }
}

// Initialization on load
window.addEventListener('DOMContentLoaded', () => {
  loadStatus();
  loadEngines();
});

