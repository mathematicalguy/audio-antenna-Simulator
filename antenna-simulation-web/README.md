# Antenna Simulation Web Application

This project is an interactive antenna simulation and audio graph display web application. It allows users to upload audio files and visualize the corresponding antenna behavior and audio waveform.

## Project Structure

```
antenna-simulation-web
├── src
│   ├── static
│   │   ├── css
│   │   │   └── styles.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── base.html
│   │   └── index.html
│   ├── antenna
│   │   ├── __init__.py
│   │   ├── simulation.py
│   │   └── visualization.py
│   ├── audio
│   │   ├── __init__.py
│   │   ├── processor.py
│   │   └── visualizer.py
│   ├── server
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── upload.py
│   └── app.py
├── tests
│   ├── __init__.py
│   ├── test_antenna.py
│   └── test_audio.py
├── requirements.txt
├── config.py
└── README.md
```

## Features

- **Audio File Upload**: Users can upload audio files (WAV or MP3) through a file drop box.
- **Antenna Simulation**: The application simulates antenna behavior based on the uploaded audio data.
- **Audio Visualization**: Displays the audio waveform and spectrum in real-time.
- **Interactive UI**: A user-friendly interface built with HTML, CSS, and JavaScript.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd antenna-simulation-web
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application settings in `config.py` as needed.

## Usage

1. Run the application:
   ```
   python src/app.py
   ```

2. Open your web browser and navigate to `http://127.0.0.1:5000`.

3. Use the file drop box to upload an audio file and observe the antenna simulation and audio graph.

## Testing

To run the tests for the antenna simulation and audio processing, use:
```
pytest tests/
```

## License

This project is licensed under the MIT License. See the LICENSE file for more details.