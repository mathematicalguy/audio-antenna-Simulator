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

class AntennaVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.frames = [];
        this.currentFrame = 0;
        this.duration = 0;
        this.frameCount = 0;
        this.playing = false;
        this.setupViewer();
    }

    setupViewer() {
        // Create image element for visualization
        this.imageElement = document.createElement('img');
        this.imageElement.style.width = '100%';
        this.imageElement.style.height = '100%';
        this.imageElement.style.objectFit = 'contain';
        this.container.appendChild(this.imageElement);

        // Create control panel
        const controls = document.createElement('div');
        controls.className = 'visualization-controls';
        
        // Play/Pause button
        this.playButton = document.createElement('button');
        this.playButton.className = 'btn btn-primary me-2';
        this.playButton.innerHTML = '▶️ Play';
        this.playButton.onclick = () => this.togglePlayback();
        
        // Timeline slider
        this.timeSlider = document.createElement('input');
        this.timeSlider.type = 'range';
        this.timeSlider.className = 'form-range';
        this.timeSlider.min = 0;
        this.timeSlider.max = 100;
        this.timeSlider.value = 0;
        this.timeSlider.oninput = (e) => this.seekTo(e.target.value);
        
        controls.appendChild(this.playButton);
        controls.appendChild(this.timeSlider);
        this.container.appendChild(controls);
    }

    setFrames(frames, duration) {
        this.frames = frames;
        this.duration = duration;
        this.frameCount = frames.length;
        this.currentFrame = 0;
        this.playing = false;
        this.updateFrame();
    }

    updateFrame() {
        if (this.currentFrame < this.frames.length) {
            this.imageElement.src = 'data:image/png;base64,' + this.frames[this.currentFrame];
            this.timeSlider.value = (this.currentFrame / (this.frameCount - 1)) * 100;
        }
    }

    togglePlayback() {
        this.playing = !this.playing;
        this.playButton.innerHTML = this.playing ? '⏸️ Pause' : '▶️ Play';
        
        if (this.playing) {
            this.animate();
        }
    }

    animate() {
        if (!this.playing) return;

        this.currentFrame = (this.currentFrame + 1) % this.frameCount;
        this.updateFrame();

        // Calculate frame rate based on duration
        const frameRate = this.duration / this.frameCount;
        setTimeout(() => this.animate(), frameRate * 1000);
    }

    seekTo(percentage) {
        this.currentFrame = Math.floor((percentage / 100) * (this.frameCount - 1));
        this.updateFrame();
    }
}

// Initialize visualizers
const waveformVisualizer = new WaveformVisualizer('waveformCanvas');
waveformVisualizer.drawWaveform(Array(100).fill(0));
const antennaVisualizer = new AntennaVisualizer('interactive3d');

document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('uploadForm');
    const resultDiv = document.getElementById('result');
    const fileInput = document.getElementById('audioFile');
    const antennaVisualization = document.getElementById('antennaVisualization');

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        resultDiv.style.display = 'none';
        antennaVisualization.style.display = 'none';

        if (!fileInput.files || fileInput.files.length === 0) {
            resultDiv.textContent = 'Please select a file';
            resultDiv.className = 'alert alert-warning';
            resultDiv.style.display = 'block';
            return;
        }

        const formData = new FormData();
        formData.append('audio', fileInput.files[0]);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (response.ok) {
                resultDiv.textContent = 'Upload successful!';
                resultDiv.className = 'alert alert-success';
                
                // Update antenna visualization
                if (data.visualizationFrames) {
                    antennaVisualizer.setFrames(data.visualizationFrames, data.duration);
                    antennaVisualization.style.display = 'block';
                }
                
                // Update waveform
                if (data.audioPlot) {
                    const img = new Image();
                    img.src = 'data:image/png;base64,' + data.audioPlot;
                    img.onload = function() {
                        const canvas = document.getElementById('waveformCanvas');
                        const ctx = canvas.getContext('2d');
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                    };
                }
            } else {
                resultDiv.textContent = data.error || 'Upload failed';
                resultDiv.className = 'alert alert-danger';
            }
        } catch (error) {
            console.error('Upload error:', error);
            resultDiv.textContent = 'Upload failed: ' + error.message;
            resultDiv.className = 'alert alert-danger';
        }

        resultDiv.style.display = 'block';
    });
});