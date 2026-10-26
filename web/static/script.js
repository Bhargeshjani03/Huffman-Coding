
const themeBtn = document.getElementById("themeBtn");
const runBtn = document.getElementById("runBtn");
const statusText = document.getElementById("status");

function updateText(id, value) {
    document.getElementById(id).textContent = value;
}

function formatSize(bytes) {
    return (bytes / 1024).toFixed(2) + " KiB";
}

function formatCheck(value) {
    return value ? "✓ PASS" : "✕ FAIL";
}

function updateCheck(id, value) {
    const element = document.getElementById(id);

    element.textContent = formatCheck(value);
    element.className = value ? "pass" : "fail";
}

function displayResults(data) {
    updateText("originalSize", formatSize(data.original_size));
    updateText("compressedSize", formatSize(data.compressed_size));

    updateText(
        "compressionRatio",
        data.compression_ratio.toFixed(4) + "×"
    );

    updateText(
        "spaceSaved",
        data.space_saved_percent.toFixed(2) + "%"
    );

    updateText(
        "accuracyBefore",
        data.accuracy_before.toFixed(2) + "%"
    );

    updateText(
        "accuracyAfter",
        data.accuracy_after.toFixed(2) + "%"
    );

    updateCheck("bytesIdentical", data.bytes_identical);
    updateCheck("weightsIdentical", data.weights_identical);
    updateCheck("predictionsIdentical", data.predictions_identical);

    updateText("tensorCount", data.tensor_count);

    updateText(
        "encodingTime",
        data.encoding_seconds.toFixed(4) + " s"
    );

    updateText(
        "decodingTime",
        data.decoding_seconds.toFixed(4) + " s"
    );

    const maximum = Math.max(
        data.original_size,
        data.compressed_size
    );

    const originalPercent = data.original_size / maximum * 100;
    const compressedPercent = data.compressed_size / maximum * 100;

    document.getElementById("originalBar").style.width =
        originalPercent + "%";

    document.getElementById("compressedBar").style.width =
        compressedPercent + "%";

    updateText("originalBarValue", formatSize(data.original_size));
    updateText("compressedBarValue", formatSize(data.compressed_size));

    const verified = data.bytes_identical
        && data.weights_identical
        && data.predictions_identical;

    statusText.textContent = verified
        ? "✓ Lossless compression and model verification passed"
        : "✕ Verification failed — check results";
}

async function loadResults() {
    try {
        const response = await fetch("/api/results");
        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Cannot load results");
        }

        displayResults(data);

    } catch (error) {
        statusText.textContent = "Error: " + error.message;
    }
}

runBtn.addEventListener("click", async () => {
    runBtn.disabled = true;
    statusText.textContent = "Running Huffman compression...";

    try {
        const response = await fetch("/api/run", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.error || "Compression failed");
        }

        displayResults(data);

    } catch (error) {
        statusText.textContent = "Error: " + error.message;
    } finally {
        runBtn.disabled = false;
    }
});

themeBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    const dark = document.body.classList.contains("dark");

    themeBtn.textContent = dark
        ? "☀ Light Mode"
        : "☾ Dark Mode";
});

loadResults();
