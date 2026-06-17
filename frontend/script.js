// Live production script tracking
document.getElementById("analyzeForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const resumeFile = document.getElementById("resume").files[0];
    const jdFile = document.getElementById("jd").files[0];
    
    const submitBtn = document.getElementById("submitBtn");
    const spinner = document.getElementById("loadingSpinner");
    const errorBox = document.getElementById("errorMessage");
    const resultContainer = document.getElementById("resultContainer");
    const analysisOutput = document.getElementById("analysisOutput");

    // Elements for the match percentage circle indicator
    const matchScoreContainer = document.getElementById("matchScoreContainer");
    const scoreRing = document.getElementById("scoreProgressRing");
    const percentText = document.getElementById("matchPercentageText");

    // Validation
    if (!resumeFile || !jdFile) {
        errorBox.innerText = "Please upload both Resume and JD PDFs.";
        errorBox.style.display = "block";
        return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("jd", jdFile);

    // UI Reset on Submit
    errorBox.style.display = "none";
    resultContainer.style.display = "none";
    matchScoreContainer.style.display = "none"; // Hide previous metrics on recalculation
    spinner.style.display = "block";
    submitBtn.disabled = true;
    submitBtn.innerText = "Analyzing... Please wait.";

    try {
        // FIXED: Replaced hardcoded local IP address with a relative production path
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        // Structural fix: throwing an explicit error safely forwards control to catch block
        if (!response.ok) {
            throw new Error(data.error || `Server responded with status ${response.status}`);
        }

        const rawText = data.analysis;

        // --- EXTRACT AND ANIMATE MATCH PERCENTAGE ---
        const match = rawText.match(/(\d{1,3})\s*%/);

        if (match && match[1]) {
            let score = parseInt(match[1], 10);
            // Safeguard boundaries between 0% and 100%
            score = Math.min(Math.max(score, 0), 100);

            matchScoreContainer.style.display = "flex";
            percentText.innerText = score + "%";
            
            // Circumference calculation of a circle with radius 50 = 2 * PI * 50 ≈ 314
            const circumference = 2 * Math.PI * 50;
            const offset = circumference - (score / 100) * circumference;
            
            // Establish visual circumference layout settings
            scoreRing.style.strokeDasharray = circumference;
            
            // Micro-timeout ensures CSS layout pipeline executes animation transition smoothly
            setTimeout(() => {
                scoreRing.style.strokeDashoffset = offset;
            }, 50);

            // Apply specific accent colors on the progress indicator contextually
            if (score >= 80) {
                scoreRing.style.stroke = "#10b981"; // Emerald Green for high match
                percentText.style.color = "#10b981";
            } else if (score >= 50) {
                scoreRing.style.stroke = "#a855f7"; // Vibrant Purple for medium match
                percentText.style.color = "#a855f7";
            } else {
                scoreRing.style.stroke = "#ef4444"; // System Red for low match
                percentText.style.color = "#ef4444";
            }
        }

        // Use Marked.js to parse markdown natively into clean HTML
        if (typeof marked !== 'undefined') {
            analysisOutput.innerHTML = marked.parse(rawText);
        } else {
            // Emergency layout text fallback if CDN script links fail to mount
            analysisOutput.innerText = rawText;
        }

        resultContainer.style.display = "block";

    } catch (error) {
        errorBox.innerText = "Error: " + error.message;
        errorBox.style.display = "block";
    } finally {
        // UI Clean up execution
        spinner.style.display = "none";
        submitBtn.disabled = false;
        submitBtn.innerText = "Analyze Match";
    }
});