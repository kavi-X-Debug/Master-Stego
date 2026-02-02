const form = document.getElementById("analyze-form");
const fileInput = document.getElementById("image-input");
const resetButton = document.getElementById("reset-button");
const statusText = document.getElementById("status-text");
const loadingOverlay = document.getElementById("loading-overlay");
const flagsContainer = document.getElementById("flags-container");
const flagPatternInput = document.getElementById("flag-pattern-input");
const flagSearchButton = document.getElementById("flag-search-button");
const customFlagsContainer = document.getElementById("custom-flags-container");

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
const outguessPanel = document.getElementById("outguess-panel");
const compressionPanel = document.getElementById("compression-panel");
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
    setStatus("Idle.");

    fileInfoPanel.textContent = "";
    exifPanel.textContent = "";
    headerFooterPanel.textContent = "";
    binwalkPanel.textContent = "";
    lsbPanel.textContent = "";
    zstegPanel.textContent = "";
    steghidePanel.textContent = "";
    outguessPanel.textContent = "";
    compressionPanel.textContent = "";
    encodingsPanel.textContent = "";

    stringsPanel.innerHTML = "";
    channelsPanel.innerHTML = "";
    enhancementsPanel.innerHTML = "";
    bitplanesPanel.innerHTML = "";

    flagsContainer.innerHTML = '<p class="text-gray-500">No flags detected yet.</p>';
    customFlagsContainer.innerHTML = '<p class="text-gray-500">No custom pattern searched.</p>';

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
    renderJson(binwalkPanel, result.binwalk);
    renderJson(lsbPanel, result.lsb);
    renderJson(zstegPanel, result.zsteg);
    renderJson(steghidePanel, result.steghide);
    renderJson(outguessPanel, result.outguess_openstego);
    renderJson(compressionPanel, result.compression);
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


switchTab("file-info");

