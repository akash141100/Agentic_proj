document.getElementById('evalForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const jd = document.getElementById('jd').value;
    const resumeFile = document.getElementById('resume').files[0];
    const submitBtn = document.getElementById('submitBtn');
    const loadingBlock = document.getElementById('loading');
    const resultsBlock = document.getElementById('results');
    const formBlock = document.getElementById('evalForm');

    // UI State Management
    submitBtn.disabled = true;
    submitBtn.querySelector('span').textContent = 'Analyzing...';
    
    // Hide results and show loader
    resultsBlock.classList.add('hidden');
    loadingBlock.classList.remove('hidden');

    const formData = new FormData();
    formData.append('jd', jd);
    formData.append('resume', resumeFile);

    try {
        const response = await fetch('https://ai-powered-resume-evaluator-15a7.onrender.com', {

            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || `Server Error: ${response.statusText}`);
        }

        const data = await response.json();

        // Populate DOM elements
        const matchSpan = document.getElementById('matchScore');
        matchSpan.textContent = data.overall_match;
        
        // Dynamic color styling for the match score
        matchSpan.className = ''; 
        if(data.overall_match === 'High') matchSpan.classList.add('match-high');
        else if(data.overall_match === 'Medium') matchSpan.classList.add('match-medium');
        else matchSpan.classList.add('match-low');

        document.getElementById('qualifications').textContent = data.qualification_match;
        document.getElementById('skills').textContent = data.skill_match;
        document.getElementById('experience').textContent = data.experience_match;

        // Force a small reflow to ensure CSS animations trigger beautifully
        void resultsBlock.offsetWidth; 

        loadingBlock.classList.add('hidden');
        resultsBlock.classList.remove('hidden');

    } catch (error) {
        console.error('Evaluation failed:', error);
        alert(error.message || 'An error occurred during evaluation.');
        loadingBlock.classList.add('hidden');
    } finally {
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = 'Analyze Candidate';
    }
});
