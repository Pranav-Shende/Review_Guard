const reviewInput = document.getElementById("reviewInput");
const counter = document.getElementById("counter");
const analyzeBtn = document.getElementById("analyzeBtn");
const buttonText = document.getElementById("buttonText");
const spinner = document.getElementById("spinner");
const resultSection = document.getElementById("resultSection");
const errorBox = document.getElementById("errorBox");

reviewInput.addEventListener("input", () => {
    counter.textContent = `${reviewInput.value.length} / 10000`;
});

async function analyzeReview() {
    const review = reviewInput.value.trim();

    errorBox.classList.add("hidden");

    if (!review) {
        showError("Please enter a review first.");
        return;
    }

    analyzeBtn.disabled = true;
    buttonText.classList.add("hidden");
    spinner.classList.remove("hidden");

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ review })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed.");
        }

        showResult(data);
    } catch (error) {
        showError(error.message);
    } finally {
        analyzeBtn.disabled = false;
        buttonText.classList.remove("hidden");
        spinner.classList.add("hidden");
    }
}

function showResult(data) {
    resultSection.classList.remove("hidden");

    const prediction = document.getElementById("prediction");
    const icon = document.getElementById("resultIcon");

    prediction.textContent = data.prediction;
    document.getElementById("confidence").textContent = `${data.confidence}%`;
    document.getElementById("genuineProbability").textContent = `${data.genuine_probability}%`;
    document.getElementById("fakeProbability").textContent = `${data.fake_probability}%`;
    document.getElementById("charCount").textContent = data.review_length;
    document.getElementById("wordCount").textContent = data.word_count;

    document.getElementById("progressBar").style.width = `${data.confidence}%`;

    if (data.class === "fake") {
        prediction.style.color = "#c33c3c";
        icon.textContent = "!";
        icon.style.background = "#fff0f0";
        icon.style.color = "#c33c3c";
    } else {
        prediction.style.color = "#208653";
        icon.textContent = "✓";
        icon.style.background = "#eaf8f0";
        icon.style.color = "#208653";
    }

    resultSection.scrollIntoView({ behavior: "smooth", block: "center" });
}

function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
}

function toggleTheme() {
    document.body.classList.toggle("light-theme");

    const button = document.getElementById("themeToggle");

    if (document.body.classList.contains("light-theme")) {
        button.textContent = "🌙";
        localStorage.setItem("theme", "light");
    } else {
        button.textContent = "☀️";
        localStorage.setItem("theme", "dark");
    }
}

window.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme");
    const button = document.getElementById("themeToggle");

    if (savedTheme === "light") {
        document.body.classList.add("light-theme");
        button.textContent = "🌙";
    }
});