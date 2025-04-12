class WaveformVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.setupCanvas();
    }

    setupCanvas() {
        // Set up canvas scaling for retina displays
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.scale(dpr, dpr);
        
        this.canvas.style.width = `${rect.width}px`;
        this.canvas.style.height = `${rect.height}px`;
    }

    drawWaveform(data) {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        this.ctx.clearRect(0, 0, width, height);
        
        // Draw background grid
        this.drawGrid();
        
        // Draw waveform
        this.ctx.beginPath();
        this.ctx.strokeStyle = '#2196F3';
        this.ctx.lineWidth = 2;
        
        const step = width / data.length;
        
        for(let i = 0; i < data.length; i++) {
            const x = i * step;
            const y = (height/2) * (1 + data[i]);
            if(i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        this.ctx.stroke();
    }

    drawGrid() {
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        this.ctx.strokeStyle = '#eee';
        this.ctx.lineWidth = 1;
        
        // Draw horizontal lines
        for(let i = 0; i < height; i += 20) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, i);
            this.ctx.lineTo(width, i);
            this.ctx.stroke();
        }
        
        // Draw vertical lines
        for(let i = 0; i < width; i += 20) {
            this.ctx.beginPath();
            this.ctx.moveTo(i, 0);
            this.ctx.lineTo(i, height);
            this.ctx.stroke();
        }
    }
}

// Initialize visualizer
const visualizer = new WaveformVisualizer('waveformCanvas');
visualizer.drawWaveform(Array(100).fill(0)); // Draw initial blank waveform

// Handle form submission
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('audioFile');
    const resultDiv = document.getElementById('result');
    
    formData.append('audio', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        resultDiv.style.display = 'block';
        
        if (response.ok) {
            resultDiv.className = 'alert alert-success';
            resultDiv.textContent = 'File uploaded successfully!';
            // Here you would update the waveform with new data
        } else {
            resultDiv.className = 'alert alert-danger';
            resultDiv.textContent = `Error: ${data.error}`;
        }
    } catch (err) {
        resultDiv.className = 'alert alert-danger';
        resultDiv.textContent = `Error: ${err.message}`;
    }
});