
"use strict";

/* =========================================================
   HUFFMAN LAB — COMPLETE DASHBOARD SCRIPT
   ========================================================= */


/* ---------- 1. GLOBAL STATE ---------- */

const $ = (id) => document.getElementById(id);

const API = {
    results: "/api/results",
    analysis: "/api/analysis",
    run: "/api/run"
};

let latestResults = null;
let latestAnalysis = null;


/* ---------- 2. FORMATTING HELPERS ---------- */

function formatBytes(bytes) {
    if (bytes === null || bytes === undefined || !Number.isFinite(Number(bytes))) {
        return "--";
    }

    const value = Number(bytes);

    if (value < 1024) {
        return `${value.toLocaleString()} B`;
    }

    if (value < 1024 * 1024) {
        return `${(value / 1024).toFixed(2)} KiB`;
    }

    return `${(value / (1024 * 1024)).toFixed(2)} MiB`;
}


function formatSeconds(seconds) {
    if (seconds === null || seconds === undefined || !Number.isFinite(Number(seconds))) {
        return "--";
    }

    return `${Number(seconds).toFixed(4)} s`;
}


function formatNumber(value, decimals = 2) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) {
        return "--";
    }

    return Number(value).toLocaleString(undefined, {
        maximumFractionDigits: decimals
    });
}


function formatPercent(value) {
    if (value === null || value === undefined || !Number.isFinite(Number(value))) {
        return "--";
    }

    return `${Number(value).toFixed(2)}%`;
}


function setText(id, value) {
    const element = $(id);

    if (element) {
        element.textContent = value ?? "--";
    }
}


function setBar(id, percentage) {
    const element = $(id);

    if (!element) return;

    const safePercentage = Math.max(
        0,
        Math.min(100, Number(percentage) || 0)
    );

    element.style.width = `${safePercentage}%`;
}


/* ---------- 3. STATUS ---------- */

function showStatus(message, type = "") {
    const status = $("status");

    if (!status) return;

    status.textContent = message;
    status.className = "status-message";

    if (type) {
        status.classList.add(type);
    }
}


/* ---------- 4. API REQUEST HELPER ---------- */

async function fetchJSON(url, options = {}) {

    const response = await fetch(url, options);

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error(`Invalid response received from ${url}`);
    }

    if (!response.ok || data.success === false) {
        throw new Error(
            data.error || `Request failed with status ${response.status}`
        );
    }

    return data;
}


/* =========================================================
   5. RESULTS API
   ========================================================= */

async function loadResults() {

    const data = await fetchJSON(API.results);

    latestResults = data;

    renderResults(data);

    return data;
}


/* ---------- 6. RENDER OVERVIEW ---------- */

function renderResults(data) {

    const originalSize = Number(data.original_size);
    const compressedSize = Number(data.compressed_size);

    const ratio = Number(data.compression_ratio);
    const saved = Number(data.space_saved_percent);


    // Main metric cards

    setText("originalSize", formatBytes(originalSize));

    setText("compressedSize", formatBytes(compressedSize));

    setText(
        "compressionRatio",
        Number.isFinite(ratio) ? `${ratio.toFixed(3)}×` : "--"
    );

    setText("spaceSaved", formatPercent(saved));


    // Size comparison

    setText("originalBarValue", formatBytes(originalSize));

    setText("compressedBarValue", formatBytes(compressedSize));

    if (
        Number.isFinite(originalSize) &&
        Number.isFinite(compressedSize) &&
        originalSize > 0
    ) {

        const maximum = Math.max(originalSize, compressedSize);

        setBar("originalBar", originalSize / maximum * 100);

        setBar("compressedBar", compressedSize / maximum * 100);
    }


    // Accuracy

    setText("accuracyBefore", formatPercent(data.accuracy_before));

    setText("accuracyAfter", formatPercent(data.accuracy_after));

    setText(
        "verificationAccuracyBefore",
        formatPercent(data.accuracy_before)
    );

    setText(
        "verificationAccuracyAfter",
        formatPercent(data.accuracy_after)
    );


    // Verification checks

    setVerification("bytesIdentical", data.bytes_identical);

    setVerification("weightsIdentical", data.weights_identical);

    setVerification("predictionsIdentical", data.predictions_identical);

    setVerification("bytesIdenticalDetail", data.bytes_identical);

    setVerification("weightsIdenticalDetail", data.weights_identical);

    setVerification("predictionsIdenticalDetail", data.predictions_identical);


    // IMPORTANT:
    // The backend uses encoding_seconds and decoding_seconds.

    const encoding = Number(data.encoding_seconds);

    const decoding = Number(data.decoding_seconds);

    setText("encodingTime", formatSeconds(encoding));

    setText("decodingTime", formatSeconds(decoding));

    setText("encodingBarValue", formatSeconds(encoding));

    setText("decodingBarValue", formatSeconds(decoding));

    if (
        Number.isFinite(encoding) &&
        Number.isFinite(decoding) &&
        Math.max(encoding, decoding) > 0
    ) {

        const maximum = Math.max(encoding, decoding);

        setBar("encodingBar", encoding / maximum * 100);

        setBar("decodingBar", decoding / maximum * 100);

    } else {

        setBar("encodingBar", 0);

        setBar("decodingBar", 0);
    }


    // Update status

    if (
        data.bytes_identical === true &&
        data.weights_identical === true &&
        data.predictions_identical === true
    ) {

        showStatus(
            "Compression results loaded. All lossless verification checks passed.",
            "success"
        );

    } else {

        showStatus(
            "Results loaded. One or more verification checks have not passed.",
            "error"
        );
    }
}


function setVerification(id, value) {

    const element = $(id);

    if (!element) return;

    const passed = value === true;

    element.textContent = passed ? "PASS" : "FAIL";

    element.classList.toggle("failed", !passed);
}


/* =========================================================
   7. HUFFMAN ANALYSIS API
   ========================================================= */

async function loadAnalysis() {

    const data = await fetchJSON(API.analysis);

    latestAnalysis = data;

    renderAnalysis(data);

    return data;
}


/* ---------- 8. RENDER ANALYSIS ---------- */

function renderAnalysis(data) {

    setText(
        "analysisTotalBytes",
        formatBytes(data.total_bytes)
    );

    setText(
        "distinctSymbols",
        formatNumber(data.distinct_symbols, 0)
    );

    setText(
        "averageCodeLength",
        Number.isFinite(Number(data.average_code_length))
            ? `${Number(data.average_code_length).toFixed(4)} bits`
            : "--"
    );

    setText(
        "theoreticalBits",
        Number.isFinite(Number(data.theoretical_encoded_bits))
            ? `${formatNumber(data.theoretical_encoded_bits, 0)} bits`
            : "--"
    );


    // Visualisations

    renderFrequencyChart(data.frequency_distribution || []);

    renderCodebook(data.codebook || []);

    renderHuffmanTree(data.tree || null);

    renderContainerComposition(data);
}


/* =========================================================
   9. ACTUAL CONTAINER COMPOSITION
   ========================================================= */

function renderContainerComposition(data) {

    const payloadSize = Number(data.encoded_payload_size);

    const overheadSize = Number(data.container_overhead);

    const payloadPercentage = Number(data.payload_percentage);

    const overheadPercentage = Number(data.overhead_percentage);

    const headerSize = Number(data.header_size);

    const metadataSize = Number(data.metadata_size);

    const totalSize = Number(data.total_container_size);


    // Validate API data.

    const valid =
        Number.isFinite(payloadSize) &&
        Number.isFinite(overheadSize) &&
        Number.isFinite(payloadPercentage) &&
        Number.isFinite(overheadPercentage) &&
        Number.isFinite(headerSize) &&
        Number.isFinite(metadataSize) &&
        Number.isFinite(totalSize) &&
        payloadSize >= 0 &&
        overheadSize >= 0 &&
        totalSize > 0 &&
        payloadSize + overheadSize === totalSize;


    if (!valid) {

        setText("compositionPercent", "N/A");

        setText("payloadSize", "Unavailable");

        setText("overheadSize", "Unavailable");

        const ring = $("compositionRing");

        if (ring) {
            ring.style.background = "var(--surface-3)";
        }

        return;
    }


    // Payload information

    setText(
        "compositionPercent",
        `${payloadPercentage.toFixed(1)}%`
    );

    setText(
        "payloadSize",
        `${formatBytes(payloadSize)} (${payloadPercentage.toFixed(2)}%)`
    );


    // Header + metadata overhead

    setText(
        "overheadSize",
        `${formatBytes(overheadSize)} (${overheadPercentage.toFixed(2)}%)`
    );


    // Donut chart

    const ring = $("compositionRing");

    if (ring) {

        const payloadDegrees = payloadPercentage * 3.6;

        ring.style.background = `
            conic-gradient(
                var(--cyan) 0deg ${payloadDegrees}deg,
                var(--surface-3) ${payloadDegrees}deg 360deg
            )
        `;
    }


    // Keep the exact components available in the browser console
    // for debugging and demonstration.

    console.info("HUFC Container Composition:", {
        header_size: headerSize,
        metadata_size: metadataSize,
        encoded_payload_size: payloadSize,
        container_overhead: overheadSize,
        total_container_size: totalSize,
        payload_percentage: payloadPercentage,
        overhead_percentage: overheadPercentage
    });
}


/* =========================================================
   10. FREQUENCY DISTRIBUTION
   ========================================================= */

function renderFrequencyChart(frequencies) {

    const container = $("frequencyChart");

    if (!container) return;

    container.replaceChildren();

    if (!frequencies.length) {

        const empty = document.createElement("div");

        empty.className = "empty-state";

        empty.textContent = "No frequency distribution available.";

        container.appendChild(empty);

        return;
    }


    const maximum = Math.max(
        ...frequencies.map(item => Number(item.frequency) || 0)
    );


    frequencies.forEach(item => {

        const row = document.createElement("div");

        row.className = "frequency-row";


        const symbol = document.createElement("div");

        symbol.className = "frequency-symbol";

        symbol.textContent = item.hex || "--";


        const track = document.createElement("div");

        track.className = "frequency-track";


        const fill = document.createElement("div");

        fill.className = "frequency-fill";

        const frequency = Number(item.frequency) || 0;

        fill.style.width = maximum > 0
            ? `${frequency / maximum * 100}%`
            : "0%";

        track.appendChild(fill);


        const value = document.createElement("div");

        value.className = "frequency-value";

        value.textContent =
            `${frequency.toLocaleString()} (${formatPercent(item.percentage)})`;


        row.append(symbol, track, value);

        container.appendChild(row);
    });
}


/* =========================================================
   11. HUFFMAN CODEBOOK
   ========================================================= */

function renderCodebook(codebook) {

    const tbody = $("codebookBody");

    if (!tbody) return;

    tbody.replaceChildren();


    if (!codebook.length) {

        const row = document.createElement("tr");

        const cell = document.createElement("td");

        cell.colSpan = 5;

        cell.className = "empty-table";

        cell.textContent = "No codebook data available.";

        row.appendChild(cell);

        tbody.appendChild(row);

        return;
    }


    codebook.forEach(item => {

        const row = document.createElement("tr");

        const values = [
            item.symbol ?? "--",
            item.hex ?? "--",
            Number(item.frequency).toLocaleString(),
            item.code ?? "--",
            item.code_length ?? "--"
        ];


        values.forEach(value => {

            const cell = document.createElement("td");

            cell.textContent = String(value);

            row.appendChild(cell);
        });


        tbody.appendChild(row);
    });
}


/* =========================================================
   12. HUFFMAN TREE VISUALIZATION
   ========================================================= */

function renderHuffmanTree(tree) {

    const container = $("huffmanTree");

    if (!container) return;

    container.replaceChildren();


    if (!tree || typeof tree !== "object") {

        const empty = document.createElement("div");

        empty.className = "empty-state";

        empty.textContent = "No Huffman tree available.";

        container.appendChild(empty);

        return;
    }


    const SVG_NS = "http://www.w3.org/2000/svg";

    const MAX_DEPTH = 5;

    let leafCounter = 0;

    const nodes = [];

    const edges = [];


    function layout(node, depth = 0, parent = null, branch = null) {

        if (!node) return null;

        const isLeaf =
            node.symbol !== null &&
            node.symbol !== undefined;

        const isTruncated = depth >= MAX_DEPTH && !isLeaf;


        const current = {

            source: node,

            depth,

            x: 0,

            y: depth * 95 + 35,

            isLeaf,

            isTruncated,

            children: []
        };


        nodes.push(current);


        if (parent) {

            edges.push({
                parent,
                child: current,
                branch
            });
        }


        if (isLeaf || isTruncated) {

            current.x = leafCounter * 85 + 45;

            leafCounter++;

            return current;
        }


        const left = layout(
            node.left,
            depth + 1,
            current,
            "0"
        );

        const right = layout(
            node.right,
            depth + 1,
            current,
            "1"
        );


        if (left) current.children.push(left);

        if (right) current.children.push(right);


        if (current.children.length === 2) {

            current.x = (
                current.children[0].x +
                current.children[1].x
            ) / 2;

        } else if (current.children.length === 1) {

            current.x = current.children[0].x;

        } else {

            current.x = leafCounter * 85 + 45;

            leafCounter++;
        }


        return current;
    }


    layout(tree);


    const width = Math.max(300, leafCounter * 85 + 40);

    const height = Math.max(
        180,
        (Math.min(MAX_DEPTH, getTreeDepth(tree)) + 1) * 95 + 25
    );


    const svg = document.createElementNS(SVG_NS, "svg");

    svg.setAttribute("width", width);

    svg.setAttribute("height", height);

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

    svg.setAttribute("role", "img");

    svg.setAttribute("aria-label", "Huffman tree visualization");


    // Draw edges first.

    edges.forEach(edge => {

        const line = document.createElementNS(SVG_NS, "line");

        line.setAttribute("x1", edge.parent.x);

        line.setAttribute("y1", edge.parent.y + 15);

        line.setAttribute("x2", edge.child.x);

        line.setAttribute("y2", edge.child.y - 15);

        line.setAttribute("class", "tree-edge");

        svg.appendChild(line);


        const label = document.createElementNS(SVG_NS, "text");

        label.setAttribute(
            "x",
            (edge.parent.x + edge.child.x) / 2 + 7
        );

        label.setAttribute(
            "y",
            (edge.parent.y + edge.child.y) / 2
        );

        label.setAttribute("class", "tree-edge-label");

        label.textContent = edge.branch;

        svg.appendChild(label);
    });


    // Draw nodes.

    nodes.forEach(node => {

        const circle = document.createElementNS(SVG_NS, "circle");

        circle.setAttribute("cx", node.x);

        circle.setAttribute("cy", node.y);

        circle.setAttribute("r", 17);

        circle.setAttribute(
            "class",
            node.isLeaf ? "tree-node tree-leaf" : "tree-node"
        );

        svg.appendChild(circle);


        const text = document.createElementNS(SVG_NS, "text");

        text.setAttribute("x", node.x);

        text.setAttribute("y", node.y);

        text.setAttribute("class", "tree-node-text");


        let label;

        if (node.isLeaf) {

            label = Number(node.source.symbol)
                .toString(16)
                .toUpperCase();

        } else if (node.isTruncated) {

            label = "...";

        } else {

            label = Number(node.source.frequency).toLocaleString();
        }


        text.textContent = label;

        svg.appendChild(text);


        const title = document.createElementNS(SVG_NS, "title");

        title.textContent = node.isLeaf
            ? `Symbol: ${node.source.symbol}, Frequency: ${node.source.frequency}`
            : `Frequency: ${node.source.frequency}`;

        circle.appendChild(title);
    });


    container.appendChild(svg);
}


function getTreeDepth(node) {

    if (!node) return 0;

    return 1 + Math.max(
        getTreeDepth(node.left),
        getTreeDepth(node.right)
    );
}


/* =========================================================
   13. THEME MANAGEMENT
   ========================================================= */

function initializeTheme() {

    const savedTheme = localStorage.getItem("huffman-theme");

    const theme = savedTheme === "light" ? "light" : "dark";

    applyTheme(theme);
}


function applyTheme(theme) {

    document.documentElement.setAttribute("data-theme", theme);

    localStorage.setItem("huffman-theme", theme);

    setText(
        "themeIcon",
        theme === "dark" ? "☀" : "☾"
    );

    setText(
        "themeText",
        theme === "dark" ? "Light mode" : "Dark mode"
    );
}


function toggleTheme() {

    const current =
        document.documentElement.getAttribute("data-theme");

    const next = current === "dark" ? "light" : "dark";

    applyTheme(next);
}


/* =========================================================
   14. SIDEBAR NAVIGATION
   ========================================================= */

function initializeNavigation() {

    const links = document.querySelectorAll(".nav-link");

    const sections = document.querySelectorAll(".dashboard-section");

    const heading = $("pageHeading");

    const currentPage = $("currentPage");


    function activateSection(sectionId) {

        links.forEach(link => {

            const active =
                link.getAttribute("href") === `#${sectionId}`;

            link.classList.toggle("active", active);

            if (active) {

                const label =
                    link.querySelector("span:last-child")?.textContent;

                if (heading && label) {
                    heading.textContent = label;
                }

                if (currentPage && label) {
                    currentPage.textContent = label.toUpperCase();
                }
            }
        });
    }


    links.forEach(link => {

        link.addEventListener("click", event => {

            const targetId = link.getAttribute("href").slice(1);

            const target = $(targetId);

            if (!target) return;

            event.preventDefault();

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

            history.replaceState(null, "", `#${targetId}`);

            activateSection(targetId);

            $("sidebar")?.classList.remove("open");
        });
    });


    const observer = new IntersectionObserver(entries => {

        const visible = entries
            .filter(entry => entry.isIntersecting)
            .sort(
                (a, b) =>
                    b.intersectionRatio - a.intersectionRatio
            );

        if (visible.length) {
            activateSection(visible[0].target.id);
        }

    }, {
        rootMargin: "-100px 0px -55% 0px",
        threshold: [0, 0.15, 0.3, 0.5]
    });


    sections.forEach(section => observer.observe(section));
}


/* =========================================================
   15. MOBILE NAVIGATION
   ========================================================= */

function initializeMobileMenu() {

    const menuButton = $("menuBtn");

    const sidebar = $("sidebar");

    if (!menuButton || !sidebar) return;


    menuButton.addEventListener("click", () => {

        sidebar.classList.toggle("open");
    });


    document.addEventListener("click", event => {

        if (
            window.innerWidth <= 760 &&
            sidebar.classList.contains("open") &&
            !sidebar.contains(event.target) &&
            !menuButton.contains(event.target)
        ) {

            sidebar.classList.remove("open");
        }
    });
}


/* =========================================================
   16. RUN COMPRESSION
   ========================================================= */

async function runCompression() {

    const button = $("runBtn");

    if (!button) return;

    button.disabled = true;

    setText("runBtnText", "Running...");

    showStatus(
        "Compression is running. This may take a few moments...",
        ""
    );


    try {

        // Run integration pipeline.

        const data = await fetchJSON(API.run, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({})
        });


        latestResults = data;

        renderResults(data);


        // Reload analysis from the newly generated HUFC file.

        await loadAnalysis();


        showStatus(
            "Compression completed successfully. All dashboard data has been refreshed.",
            "success"
        );

    } catch (error) {

        console.error("Compression failed:", error);

        showStatus(
            `Compression failed: ${error.message}`,
            "error"
        );

    } finally {

        button.disabled = false;

        setText("runBtnText", "Run Compression");
    }
}


/* =========================================================
   17. INITIALIZE DASHBOARD
   ========================================================= */

async function initializeDashboard() {

    // Initialize interface.

    initializeTheme();

    initializeNavigation();

    initializeMobileMenu();


    // Theme button.

    $("themeBtn")?.addEventListener("click", toggleTheme);


    // Compression button.

    $("runBtn")?.addEventListener("click", runCompression);


    // Load results.

    try {

        await loadResults();

    } catch (error) {

        console.error("Results loading failed:", error);

        showStatus(
            `Could not load compression results: ${error.message}`,
            "error"
        );
    }


    // Load analysis independently.

    try {

        await loadAnalysis();

    } catch (error) {

        console.error("Analysis loading failed:", error);

        const chart = $("frequencyChart");

        if (chart) {
            chart.innerHTML = `
                <div class="empty-state">
                    Could not load frequency analysis.
                </div>
            `;
        }

        const tree = $("huffmanTree");

        if (tree) {
            tree.innerHTML = `
                <div class="empty-state">
                    Could not load Huffman tree.
                </div>
            `;
        }
    }
}


/* =========================================================
   18. START APPLICATION
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    initializeDashboard
);
