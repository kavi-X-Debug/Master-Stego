const form = document.getElementById("analyze-form");
const fileInput = document.getElementById("image-input");
const steghidePassInput = document.getElementById("steghide-passphrase");
const resetButton = document.getElementById("reset-button");
const statusText = document.getElementById("status-text");
const loadingOverlay = document.getElementById("loading-overlay");
const flagsContainer = document.getElementById("flags-container");
const flagPatternInput = document.getElementById("flag-pattern-input");
const flagSearchButton = document.getElementById("flag-search-button");
const customFlagsContainer = document.getElementById("custom-flags-container");
const chatLog = document.getElementById("chat-log");
const chatInput = document.getElementById("chat-input");
const chatSendButton = document.getElementById("chat-send-button");

const tabButtons = Array.from(document.querySelectorAll(".tab-button"));
const tabPanels = Array.from(document.querySelectorAll(".tab-panel"));
const activeTabTitle = document.getElementById("active-tab-title");

const fileInfoPanel = document.getElementById("file-info-panel");
const exifPanel = document.getElementById("exif-panel");
const stringsPanel = document.getElementById("strings-panel");
const headerFooterPanel = document.getElementById("header-footer-panel");
const binwalkPanel = document.getElementById("binwalk-panel");
const channelsPanel = document.getElementById("channels-panel");
const enhancementsPanel = document.getElementById("enhancements-panel");
const bitplanesPanel = document.getElementById("bitplanes-panel");
const lsbPanel = document.getElementById("lsb-panel");
const zstegPanel = document.getElementById("zsteg-panel");
const steghidePanel = document.getElementById("steghide-panel");
const encodingsPanel = document.getElementById("encodings-panel");

let lastResult = null;


function setStatus(text) {
    statusText.textContent = text;
}


function showLoader() {
    if (loadingOverlay) {
        loadingOverlay.classList.add("active");
    }
}


function hideLoader() {
    if (loadingOverlay) {
        loadingOverlay.classList.remove("active");
    }
}


function switchTab(name) {
    tabButtons.forEach((btn) => {
        if (btn.dataset.tab === name) {
            btn.classList.add("bg-gray-800", "text-emerald-400");
        } else {
            btn.classList.remove("bg-gray-800", "text-emerald-400");
        }
    });

    tabPanels.forEach((panel) => {
        if (panel.dataset.panel === name) {
            panel.classList.remove("hidden");
        } else {
            panel.classList.add("hidden");
        }
    });

    const activeButton = tabButtons.find((b) => b.dataset.tab === name);
    if (activeButton) {
        activeTabTitle.textContent = activeButton.textContent.trim();
    }
}


tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        switchTab(btn.dataset.tab);
    });
});


function resetUI() {
    fileInput.value = "";
    if (steghidePassInput) {
        steghidePassInput.value = "";
    }
    setStatus("Idle.");

    fileInfoPanel.textContent = "";
    exifPanel.textContent = "";
    headerFooterPanel.textContent = "";
    binwalkPanel.textContent = "";
    lsbPanel.textContent = "";
    zstegPanel.textContent = "";
    steghidePanel.textContent = "";
    encodingsPanel.textContent = "";

    stringsPanel.innerHTML = "";
    channelsPanel.innerHTML = "";
    enhancementsPanel.innerHTML = "";
    bitplanesPanel.innerHTML = "";

    flagsContainer.innerHTML = '<p class="text-gray-500">No flags detected yet.</p>';
    customFlagsContainer.innerHTML = '<p class="text-gray-500">No custom pattern searched.</p>';

    if (chatLog) {
        chatLog.innerHTML = '<div class="text-gray-500">Run an analysis, then ask a question here.</div>';
    }

    switchTab("file-info");
    hideLoader();
}


resetButton.addEventListener("click", () => {
    resetUI();
});


function highlightFlags(text, flags) {
    if (!flags || !flags.length) {
        return text;
    }
    let highlighted = text;
    flags.forEach(({ flag }) => {
        const safeFlag = flag.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const re = new RegExp(safeFlag, "g");
        highlighted = highlighted.replace(re, `<span class="bg-emerald-500 text-black px-0.5 rounded">${flag}</span>`);
    });
    return highlighted;
}


function renderFlags(flagsResult) {
    flagsContainer.innerHTML = "";
    if (!flagsResult || !flagsResult.flags || !flagsResult.flags.length) {
        flagsContainer.innerHTML = `<p class="text-gray-500">No flags detected.</p>`;
        return;
    }
    flagsResult.flags.forEach((f) => {
        const div = document.createElement("div");
        div.className = "bg-gray-800 border border-emerald-600/50 rounded px-2 py-1";
        div.innerHTML = `
            <div class="text-xs font-mono text-emerald-300">${f.flag}</div>
            <div class="text-[10px] text-gray-400 mt-1">${f.source}</div>
        `;
        flagsContainer.appendChild(div);
    });
}


function appendChatBubble(role, text) {
    if (!chatLog) {
        return;
    }
    const wrapper = document.createElement("div");
    wrapper.className = "flex " + (role === "user" ? "justify-end" : "justify-start");
    const bubble = document.createElement("div");
    bubble.className =
        "max-w-[80%] px-2 py-1 rounded text-[11px] whitespace-pre-wrap break-words " +
        (role === "user"
            ? "bg-emerald-600 text-black"
            : "bg-gray-800 text-gray-100 border border-gray-700");
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    chatLog.appendChild(wrapper);
    chatLog.scrollTop = chatLog.scrollHeight;
}


async function sendChatMessage() {
    if (!chatInput || !chatLog) {
        return;
    }
    if (!lastResult) {
        appendChatBubble("assistant", "Run an analysis first, then ask about the results.");
        return;
    }
    const message = chatInput.value.trim();
    if (!message) {
        return;
    }

    appendChatBubble("user", message);
    chatInput.value = "";

    const thinkingId = "chat-thinking";
    const thinking = document.createElement("div");
    thinking.id = thinkingId;
    thinking.className = "text-[11px] text-gray-500";
    thinking.textContent = "Gemini is thinking...";
    chatLog.appendChild(thinking);
    chatLog.scrollTop = chatLog.scrollHeight;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                message,
                analysis: lastResult,
            }),
        });

        if (!response.ok) {
            const errorPayload = await response.json().catch(() => ({}));
            const msg = errorPayload.error || response.statusText || "Chat request failed.";
            appendChatBubble("assistant", msg);
            return;
        }

        const payload = await response.json();
        if (payload.reply) {
            appendChatBubble("assistant", payload.reply);
        } else if (payload.error) {
            appendChatBubble("assistant", payload.error);
        } else {
            appendChatBubble("assistant", "Received an empty response from the chatbot.");
        }
    } catch (err) {
        appendChatBubble("assistant", "Network error while contacting the chatbot.");
    } finally {
        const existingThinking = document.getElementById(thinkingId);
        if (existingThinking && existingThinking.parentNode) {
            existingThinking.parentNode.removeChild(existingThinking);
        }
    }
}


function renderCustomFlags(matches, message) {
    customFlagsContainer.innerHTML = "";
    if (message) {
        customFlagsContainer.innerHTML = `<p class="text-gray-500">${message}</p>`;
        return;
    }
    if (!matches || !matches.length) {
        customFlagsContainer.innerHTML = `<p class="text-gray-500">No matches for this pattern.</p>`;
        return;
    }
    matches.forEach((value) => {
        const div = document.createElement("div");
        div.className = "bg-gray-800/70 border border-emerald-600/40 rounded px-2 py-1 text-[11px] font-mono text-emerald-300";
        div.textContent = value;
        customFlagsContainer.appendChild(div);
    });
}


function renderJson(panel, data) {
    panel.textContent = JSON.stringify(data, null, 2);
}


function renderStringsPanel(stringsResult, flagsResult) {
    stringsPanel.innerHTML = "";
    const ascii = stringsResult.ascii || {};
    const utf16 = stringsResult.utf16 || {};

    const sections = [
        { title: "ASCII", data: ascii },
        { title: "UTF-16", data: utf16 },
    ];

    sections.forEach(({ title, data }) => {
        const wrapper = document.createElement("div");
        wrapper.className = "border border-gray-800 rounded p-2";
        const header = document.createElement("div");
        header.className = "flex justify-between items-center mb-1";
        header.innerHTML = `
            <span class="font-semibold text-emerald-400">${title}</span>
            <span class="text-[10px] text-gray-500">${data.count || 0} strings (sample)</span>
        `;
        wrapper.appendChild(header);

        const pre = document.createElement("pre");
        pre.className = "text-[11px] text-green-400 whitespace-pre-wrap break-all max-h-48 overflow-auto max-w-full";

        const lines = (data.sample || []).slice(0, 300);
        const rawText = lines.join("\n");
        pre.innerHTML = highlightFlags(rawText, flagsResult.flags);

        wrapper.appendChild(pre);
        stringsPanel.appendChild(wrapper);
    });
}


function renderLsbPanel(lsbResult, flagsResult) {
    lsbPanel.innerHTML = "";
    if (!lsbResult) {
        lsbPanel.textContent = "No LSB data.";
        return;
    }
    if (lsbResult.error) {
        lsbPanel.textContent = "LSB error: " + lsbResult.error;
        return;
    }

    const container = document.createElement("div");
    container.className = "space-y-3";

    const channels = lsbResult.channels || {};
    Object.entries(channels).forEach(([name, data]) => {
        const block = document.createElement("div");
        block.className = "border border-gray-800 rounded p-2";

        const header = document.createElement("div");
        header.className = "flex justify-between items-center mb-1";
        header.innerHTML = `
            <span class="font-semibold text-emerald-400">Channel ${name.toUpperCase()}</span>
            <span class="text-[10px] text-gray-500">${data.length || 0} chars</span>
        `;
        block.appendChild(header);

        const pre = document.createElement("pre");
        pre.className =
            "text-[11px] text-green-400 whitespace-pre-wrap break-all max-h-32 overflow-auto max-w-full";
        const preview = data.preview || "";
        pre.innerHTML = highlightFlags(preview, flagsResult.flags);
        block.appendChild(pre);

        container.appendChild(block);
    });

    const combined = lsbResult.combined || {};
    const combinedBlock = document.createElement("div");
    combinedBlock.className = "border border-gray-800 rounded p-2";
    const combinedHeader = document.createElement("div");
    combinedHeader.className = "flex justify-between items-center mb-1";
    combinedHeader.innerHTML = `
        <span class="font-semibold text-emerald-400">Combined RGB</span>
        <span class="text-[10px] text-gray-500">${combined.length || 0} chars</span>
    `;
    combinedBlock.appendChild(combinedHeader);
    const combinedPre = document.createElement("pre");
    combinedPre.className =
        "text-[11px] text-green-400 whitespace-pre-wrap break-all max-h-32 overflow-auto max-w-full";
    const combinedPreview = combined.preview || "";
    combinedPre.innerHTML = highlightFlags(combinedPreview, flagsResult.flags);
    combinedBlock.appendChild(combinedPre);
    container.appendChild(combinedBlock);

    lsbPanel.appendChild(container);
}


function renderZstegPanel(zstegResult, flagsResult) {
    zstegPanel.innerHTML = "";
    if (!zstegResult) {
        zstegPanel.textContent = "No zsteg data.";
        return;
    }
    if (zstegResult.skipped) {
        zstegPanel.textContent = "Zsteg is working for only .png Images";
        return;
    }
    if (zstegResult.error) {
        zstegPanel.textContent = "zsteg error: " + zstegResult.error;
        return;
    }

    if (zstegResult.available === false) {
        zstegPanel.textContent = "zsteg not installed on server.";
        return;
    }

    const container = document.createElement("div");
    container.className = "space-y-3";

    const stdoutBlock = document.createElement("div");
    stdoutBlock.className = "border border-gray-800 rounded p-2";
    const stdoutHeader = document.createElement("div");
    stdoutHeader.className = "flex justify-between items-center mb-1";
    stdoutHeader.innerHTML = `
        <span class="font-semibold text-emerald-400">zsteg -a output</span>
        <span class="text-[10px] text-gray-500">return code: ${zstegResult.returncode}</span>
    `;
    stdoutBlock.appendChild(stdoutHeader);
    const stdoutPre = document.createElement("pre");
    stdoutPre.className =
        "text-[11px] text-green-400 whitespace-pre-wrap break-all max-h-64 overflow-auto max-w-full";
    const stdout = zstegResult.stdout || "";
    stdoutPre.innerHTML = highlightFlags(stdout, (flagsResult && flagsResult.flags) || []);
    stdoutBlock.appendChild(stdoutPre);
    container.appendChild(stdoutBlock);

    const stderrText = zstegResult.stderr || "";
    if (stderrText && stderrText.trim()) {
        const stderrBlock = document.createElement("div");
        stderrBlock.className = "border border-gray-800 rounded p-2";
        const stderrHeader = document.createElement("div");
        stderrHeader.className = "mb-1 text-[10px] text-gray-400";
        stderrHeader.textContent = "stderr";
        stderrBlock.appendChild(stderrHeader);
        const stderrPre = document.createElement("pre");
        stderrPre.className =
            "text-[11px] text-gray-400 whitespace-pre-wrap break-all max-h-32 overflow-auto max-w-full";
        stderrPre.textContent = stderrText;
        stderrBlock.appendChild(stderrPre);
        container.appendChild(stderrBlock);
    }

    zstegPanel.appendChild(container);
}


function renderBinwalkPanel(binwalkResult, extractedFiles, flagsResult) {
    binwalkPanel.innerHTML = "";
    if (!binwalkResult) {
        binwalkPanel.textContent = "No binwalk data.";
        return;
    }
    if (binwalkResult.error) {
        binwalkPanel.textContent = "Binwalk error: " + binwalkResult.error;
        return;
    }

    if (binwalkResult.available === false) {
        binwalkPanel.textContent = "binwalk not installed on server.";
        return;
    }

    const container = document.createElement("div");
    container.className = "space-y-3";

    const summaryBlock = document.createElement("div");
    summaryBlock.className = "border border-gray-800 rounded p-2";
    const summaryHeader = document.createElement("div");
    summaryHeader.className = "flex justify-between items-center mb-1";
    summaryHeader.innerHTML = `
        <span class="font-semibold text-emerald-400">Binwalk summary</span>
        <span class="text-[10px] text-gray-500">return code: ${binwalkResult.returncode}</span>
    `;
    summaryBlock.appendChild(summaryHeader);
    const summaryPre = document.createElement("pre");
    summaryPre.className =
        "text-[11px] text-green-400 whitespace-pre-wrap break-all max-h-48 overflow-auto max-w-full";
    const summaryText = binwalkResult.summary || "";
    summaryPre.innerHTML = highlightFlags(summaryText, (flagsResult && flagsResult.flags) || []);
    summaryBlock.appendChild(summaryPre);
    container.appendChild(summaryBlock);

    const filesBlock = document.createElement("div");
    filesBlock.className = "border border-gray-800 rounded p-2";
    const filesHeader = document.createElement("div");
    filesHeader.className = "mb-1 text-[10px] text-gray-400";
    filesHeader.textContent = "Embedded files";
    filesBlock.appendChild(filesHeader);

    const paths = Array.isArray(binwalkResult.extracted_paths) ? binwalkResult.extracted_paths : [];
    if (!paths.length) {
        const none = document.createElement("div");
        none.className = "text-[11px] text-gray-500";
        none.textContent = "No embedded files extracted by binwalk.";
        filesBlock.appendChild(none);
    } else {
        const list = document.createElement("div");
        list.className = "space-y-1 text-[11px]";
        paths.forEach((relPath) => {
            const entry = (extractedFiles || []).find((e) => e.name === relPath);
            const row = document.createElement("div");
            row.className = "flex items-center justify-between";
            if (entry && entry.url) {
                const link = document.createElement("a");
                link.href = entry.url;
                link.textContent = relPath;
                link.className = "text-emerald-400 hover:text-emerald-300 break-all";
                link.target = "_blank";
                row.appendChild(link);
            } else {
                const span = document.createElement("span");
                span.textContent = relPath;
                span.className = "text-gray-300 break-all";
                row.appendChild(span);
            }
            list.appendChild(row);
        });
        filesBlock.appendChild(list);
    }

    container.appendChild(filesBlock);

    binwalkPanel.appendChild(container);
}


function renderImageGrid(container, entries, labelTransform) {
    container.innerHTML = "";
    entries.forEach((entry) => {
        const wrapper = document.createElement("div");
        wrapper.className = "bg-gray-800 rounded border border-gray-700 overflow-hidden";

        const img = document.createElement("img");
        img.src = entry.url;
        img.alt = entry.label;
        img.className = "w-full h-32 object-contain bg-black";

        const caption = document.createElement("div");
        caption.className = "px-2 py-1 text-[10px] text-gray-300 flex justify-between";
        caption.innerHTML = `<span>${labelTransform(entry.label)}</span>`;

        wrapper.appendChild(img);
        wrapper.appendChild(caption);
        container.appendChild(wrapper);
    });
}


function populatePanels(result) {
    lastResult = result;
    renderJson(fileInfoPanel, result.file_info);
    renderJson(exifPanel, result.exif);
    renderJson(headerFooterPanel, result.header_footer);
    renderBinwalkPanel(result.binwalk, result.extracted_files || [], result.flags);
    renderLsbPanel(result.lsb, result.flags);
    renderZstegPanel(result.zsteg, result.flags);
    renderJson(steghidePanel, result.steghide);
    renderJson(encodingsPanel, result.encodings);

    renderStringsPanel(result.strings, result.flags);

    const channelEntries = [];
    Object.entries(result.color_channels.channels || {}).forEach(([name, info]) => {
        channelEntries.push({ label: name.toUpperCase(), url: info.url });
    });
    renderImageGrid(channelsPanel, channelEntries, (label) => `${label} channel`);

    const enhEntries = [];
    Object.entries(result.enhancements.images || {}).forEach(([name, info]) => {
        enhEntries.push({ label: name, url: info.url });
    });
    renderImageGrid(enhancementsPanel, enhEntries, (label) => label);

    const bitEntries = [];
    Object.entries(result.bitplanes.planes || {}).forEach(([channel, bits]) => {
        Object.entries(bits).forEach(([bit, info]) => {
            bitEntries.push({ label: `${channel.toUpperCase()} bit ${bit}`, url: info.url });
        });
    });
    renderImageGrid(bitplanesPanel, bitEntries, (label) => label);

    renderFlags(result.flags);
}


form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!fileInput.files.length) {
        setStatus("Select an image first.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    if (steghidePassInput && steghidePassInput.value) {
        formData.append("steghide_passphrase", steghidePassInput.value);
    }

    setStatus("Running full analysis pipeline...");
    showLoader();

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            const errorPayload = await response.json().catch(() => ({}));
            setStatus(`Error: ${errorPayload.error || response.statusText}`);
            hideLoader();
            return;
        }

        const result = await response.json();
        populatePanels(result);
        switchTab("file-info");
        setStatus("Analysis complete.");
    } catch (err) {
        setStatus("Request failed.");
        console.error(err);
    } finally {
        hideLoader();
    }
});


function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}


function buildFlagRegex(pattern) {
    const raw = pattern.trim();
    if (!raw) {
        return null;
    }

    if (raw.includes("{}")) {
        const parts = raw.split("{}");
        const prefix = escapeRegExp(parts[0] || "");
        const suffix = escapeRegExp(parts[1] || "");
        return new RegExp(prefix + "\\{.*?\\}" + suffix, "gi");
    }

    try {
        return new RegExp(raw, "gi");
    } catch (e) {
        return null;
    }
}


function runCustomFlagSearch() {
    if (!lastResult) {
        renderCustomFlags([], "Run analysis first.");
        return;
    }

    const pattern = flagPatternInput.value || "";
    const regex = buildFlagRegex(pattern);
    if (!regex) {
        renderCustomFlags([], "Invalid pattern.");
        return;
    }

    const corpus = JSON.stringify(lastResult);
    const unique = new Set();
    let match;

    while ((match = regex.exec(corpus)) !== null) {
        if (match[0]) {
            unique.add(match[0]);
            if (unique.size >= 50) {
                break;
            }
        }
    }

    const customValues = Array.from(unique);
    renderCustomFlags(customValues);

    const existingFlags = (lastResult.flags && Array.isArray(lastResult.flags.flags)) ? lastResult.flags.flags.slice() : [];
    const seen = new Set(existingFlags.map((f) => f.flag));

    customValues.forEach((val) => {
        if (!seen.has(val)) {
            existingFlags.push({
                flag: val,
                source: "custom pattern",
            });
            seen.add(val);
        }
    });

    renderFlags({ flags: existingFlags });
}


flagSearchButton.addEventListener("click", () => {
    runCustomFlagSearch();
});


flagPatternInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        runCustomFlagSearch();
    }
});


if (chatSendButton) {
    chatSendButton.addEventListener("click", () => {
        sendChatMessage();
    });
}


if (chatInput) {
    chatInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            sendChatMessage();
        }
    });
}


switchTab("file-info");

