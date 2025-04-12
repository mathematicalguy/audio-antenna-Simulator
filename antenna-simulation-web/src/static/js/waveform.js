class WaveformVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.audioData = [];
        this.currentTime = 0;
        this.duration = 0;
        this.isPlaying = false;
        this.timeMarker = 0;
        this.setupCanvas();
        this.setupEventListeners();
    }

    setupCanvas() {
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.getBoundingClientRect();
        
        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;
        this.ctx.scale(dpr, dpr);
        
        this.canvas.style.width = `${rect.width}px`;
        this.canvas.style.height = `${rect.height}px`;
    }

    setupEventListeners() {
        this.canvas.addEventListener('click', (e) => this.handleCanvasClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.animationFrameId = null;
        this.lastFrameTime = 0;
        this.fps = 30;
        this.frameInterval = 1000 / this.fps;
    }

    handleCanvasClick(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const timePosition = (x / rect.width) * this.duration;
        this.setTime(timePosition);
        if (this.onTimeUpdate) {
            this.onTimeUpdate(timePosition);
        }
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        this.timeMarker = x;
        this.drawWaveform(this.audioData);
    }

    setTime(time) {
        this.currentTime = Math.max(0, Math.min(time, this.duration));
        const progress = this.currentTime / this.duration;
        this.timeMarker = this.canvas.width * progress;
        this.drawWaveform(this.audioData);
    }

    drawWaveform(data) {
        if (!data || !data.length) return;
        
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

        // Draw time marker
        this.ctx.beginPath();
        this.ctx.strokeStyle = '#FF4081';
        this.ctx.lineWidth = 2;
        this.ctx.moveTo(this.timeMarker, 0);
        this.ctx.lineTo(this.timeMarker, height);
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

    updateData(audioData, duration) {
        this.audioData = audioData;
        this.duration = duration;
        this.drawWaveform(audioData);
    }

    animate(currentTime) {
        if (!this.isPlaying) return;

        if (currentTime - this.lastFrameTime >= this.frameInterval) {
            this.currentTime += this.frameInterval / 1000;
            if (this.currentTime >= this.duration) {
                this.currentTime = 0;
            }

            const progress = this.currentTime / this.duration;
            this.timeMarker = this.canvas.width * progress;
            this.drawWaveform(this.audioData);

            // Update time display
            const currentTimeEl = document.getElementById('currentTime');
            const totalTimeEl = document.getElementById('totalTime');
            if (currentTimeEl) currentTimeEl.textContent = this.formatTime(this.currentTime);
            if (totalTimeEl) totalTimeEl.textContent = this.formatTime(this.duration);

            if (this.onTimeUpdate) {
                this.onTimeUpdate(this.currentTime);
            }

            this.lastFrameTime = currentTime;
        }

        this.animationFrameId = requestAnimationFrame(t => this.animate(t));
    }

    formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    togglePlayback(isPlaying) {
        this.isPlaying = isPlaying;
        if (this.isPlaying) {
            this.lastFrameTime = 0;
            this.animate(performance.now());
        } else if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
        }
    }
}

class AntennaVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.renderer = window.vtkRenderer;
        this.renderWindow = window.vtkRenderWindow;
        this.simulation = null;
        this.controls = {};
        this.isPlaying = false;
        
        // Initialize once VTK.js is ready
        if (this.renderer && this.renderWindow) {
            this.setupControls();
            this.createInitialScene();
        }
    }

    createInitialScene() {
        // Create initial field points
        const phi = vtk.Common.Core.vtkPoints.newInstance();
        const numPoints = 1000;
        
        for (let i = 0; i < numPoints; i++) {
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            const r = 0.2 + Math.random() * 1.8;
            
            const x = r * Math.sin(phi) * Math.cos(theta);
            const y = r * Math.sin(phi) * Math.sin(theta);
            const z = r * Math.cos(phi);
            
            phi.insertNextPoint(x, y, z);
        }

        // Create polydata for field points
        this.fieldData = vtk.Common.DataModel.vtkPolyData.newInstance();
        this.fieldData.setPoints(phi);

        // Create glyph for field visualization
        const sphereSource = vtk.Filters.Sources.vtkSphereSource.newInstance({
            radius: 0.02,
            phiResolution: 8,
            thetaResolution: 8
        });

        this.glyph = vtk.Filters.General.vtkGlyph3D.newInstance({
            scaleFactor: 0.1,
            scaleMode: vtk.Filters.General.vtkGlyph3D.ScaleModes.SCALE_BY_MAGNITUDE
        });
        this.glyph.setInputData(this.fieldData);
        this.glyph.setSourceConnection(sphereSource.getOutputPort());

        // Create initial antenna
        this.createAntenna();
    }

    setupControls() {
        const controls = document.createElement('div');
        controls.className = 'visualization-controls';
        
        // Create sliders
        this.controls.length = this.createSlider('Antenna Length (m)', 0.2, 2.0, 1.0, 0.1);
        this.controls.frequency = this.createSlider('Frequency (Hz)', 0.1, 5.0, 1.0, 0.1);
        this.controls.maxCurrent = this.createSlider('Max Current (A)', 0.5, 3.0, 1.0, 0.1);
        this.controls.minCurrent = this.createSlider('Min Current (A)', 0.0, 0.5, 0.1, 0.05);
        
        // Add play/pause button
        this.controls.playButton = document.createElement('button');
        this.controls.playButton.className = 'btn btn-primary';
        this.controls.playButton.innerHTML = '▶️ Play';
        this.controls.playButton.onclick = () => this.togglePlayback();
        
        // Add all controls to container
        Object.values(this.controls).forEach(control => {
            controls.appendChild(control.parentElement || control);
        });
        
        this.container.appendChild(controls);
    }

    createSlider(label, min, max, value, step) {
        const container = document.createElement('div');
        container.className = 'slider-container';
        
        const labelEl = document.createElement('label');
        labelEl.textContent = label;
        
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.className = 'form-range';
        slider.min = min;
        slider.max = max;
        slider.value = value;
        slider.step = step;
        
        container.appendChild(labelEl);
        container.appendChild(slider);
        return slider;
    }

    togglePlayback() {
        this.isPlaying = !this.isPlaying;
        this.controls.playButton.innerHTML = this.isPlaying ? '⏸️ Pause' : '▶️ Play';
        if (this.onPlaybackChange) {
            this.onPlaybackChange(this.isPlaying);
        }
        
        // Update waveform playback state
        if (window.waveformVisualizer) {
            window.waveformVisualizer.togglePlayback(this.isPlaying);
        }
    }

    updateParameters() {
        if (this.onParametersChange) {
            this.onParametersChange({
                length: parseFloat(this.controls.length.value),
                frequency: parseFloat(this.controls.frequency.value),
                maxCurrent: parseFloat(this.controls.maxCurrent.value),
                minCurrent: parseFloat(this.controls.minCurrent.value)
            });
        }
    }
}

// Initialize visualizers and make waveform visualizer globally accessible
window.waveformVisualizer = new WaveformVisualizer('waveformCanvas');
const antennaVisualizer = new AntennaVisualizer('interactive3d');

// Set up synchronization between visualizers
window.waveformVisualizer.onTimeUpdate = (time) => {
    // Update antenna visualization time
    if (antennaVisualizer.simulation) {
        antennaVisualizer.simulation.setTime(time);
    }
};

antennaVisualizer.onPlaybackChange = (isPlaying) => {
    // Synchronize playback state
    window.waveformVisualizer.togglePlayback(isPlaying);
};

antennaVisualizer.onParametersChange = (params) => {
    // Update simulation parameters
    if (antennaVisualizer.simulation) {
        antennaVisualizer.simulation.setParameters(params);
    }
};

// Handle file upload
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

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.audioData && data.duration) {
                // Show success message
                resultDiv.textContent = 'Upload successful!';
                resultDiv.className = 'alert alert-success';
                resultDiv.style.display = 'block';

                // Show visualization container
                antennaVisualization.style.display = 'block';

                // Update visualizations
                window.waveformVisualizer.updateData(data.audioData, data.duration);
            } else {
                throw new Error('Invalid response data');
            }
        } catch (error) {
            console.error('Upload error:', error);
            resultDiv.textContent = 'Upload failed: ' + error.message;
            resultDiv.className = 'alert alert-danger';
            resultDiv.style.display = 'block';
        }
    });
});