let synthesis = window.speechSynthesis;
let currentUtterance = null;

async function processImage() {
    const fileInput = document.getElementById('imageInput');
    const resultDiv = document.getElementById('ocrResult');
    
    if (!fileInput.files[0]) {
        alert('Please select an image file');
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    try {
        const response = await fetch('/api/ocr', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        resultDiv.textContent = data.text;
        updateConfidence(data.confidence * 100);
        
    } catch (error) {
        console.error('OCR Error:', error);
        alert(`Error: ${error.message}`);
    }
}

function speakText() {
    if (currentUtterance) {
        synthesis.cancel();
    }

    const text = document.getElementById('ocrResult').textContent;
    currentUtterance = new SpeechSynthesisUtterance(text);
    
    currentUtterance.lang = 'en-US';
    currentUtterance.pitch = 1;
    currentUtterance.rate = 1;
    
    synthesis.speak(currentUtterance);
}

function updateConfidence(percentage) {
    const bar = document.getElementById('confidenceBar');
    const value = document.getElementById('confidenceValue');
    
    percentage = Math.min(100, Math.max(0, percentage));
    bar.style.width = `${percentage}%`;
    value.textContent = `${Math.round(percentage)}% Confidence`;
    
    // Color coding
    if (percentage > 80) bar.style.backgroundColor = '#4CAF50';
    else if (percentage > 60) bar.style.backgroundColor = '#FFC107';
    else bar.style.backgroundColor = '#F44336';
}
