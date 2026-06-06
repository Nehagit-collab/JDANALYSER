document.getElementById("analyzeForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const resumeFile = document.getElementById("resume").files[0];
    const jdFile = document.getElementById("jd").files[0];
    
    // ✅ Updated targets to match your new modern layout elements
    const submitBtn = document.getElementById("submitBtn");
    const spinner = document.getElementById("loadingSpinner");
    const errorBox = document.getElementById("errorMessage");
    const resultContainer = document.getElementById("resultContainer");
    const analysisOutput = document.getElementById("analysisOutput");

    if (!resumeFile || !jdFile) {
        errorBox.innerText = "Please upload both Resume and JD PDFs.";
        errorBox.style.display = "block";
        return;
    }

    const formData = new FormData();
    formData.append("resume", resumeFile);
    formData.append("jd", jdFile);

    // 🔄 UI State: Reset previous errors/results, lock button, and show loading spinner
    errorBox.style.display = "none";
    resultContainer.style.display = "none";
    spinner.style.display = "block";
    submitBtn.disabled = true;
    submitBtn.innerText = "Analyzing... Please wait.";

    try {
        const response = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            errorBox.innerText = "Error: " + (data.error || "Unknown error");
            errorBox.style.display = "block";
            return;
        }

        // 🎨 COLOR CONVERSION ENGINE: 
        // Converts raw Markdown syntax into colorful HTML tags before rendering
        let rawText = data.analysis;

        let formattedHtml = rawText
            // 1. Convert bold markdown (**text**) into distinct colorful strong tags
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            
            // 2. Convert markdown headings (### Heading) into stylized h4 headers
            .replace(/### (.*?)(?:\n|$)/g, '<h4>$1</h4>')
            
            // 3. Convert markdown bullet points (* item or - item) into real clean list items
            .replace(/^\s*[\*\-]\s+(.*?)(?:\n|$)/gm, '<li>$1</li>');

        // Handle structural cleanup for consecutive <li> elements wrapped in a list context
        if (formattedHtml.includes('<li>')) {
            // Simple check to ensure line-broken lists render smoothly
            formattedHtml = formattedHtml.replace(/(<li>.*?<\/li>)/g, '<ul>$1</ul>').replace(/<\/ul>\s*<ul>/g, '');
        }

        // ✅ Inject the HTML structure using innerHTML so the CSS styling engine can colorize it
        analysisOutput.innerHTML = formattedHtml;
        resultContainer.style.display = "block";

    } catch (error) {
        errorBox.innerText = "Request failed: " + error.message;
        errorBox.style.display = "block";
    } finally {
        // 🔄 UI State Reset: Hide spinner and unlock submit button
        spinner.style.display = "none";
        submitBtn.disabled = false;
        submitBtn.innerText = "Analyze Match";
    }
});