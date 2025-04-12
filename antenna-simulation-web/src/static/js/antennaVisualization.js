class EMFieldVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.renderer = null;
        this.renderWindow = null;
        this.actor = null;
        this.fieldPoints = [];
        this.fieldVectors = [];
        this.simulation = null;
        this.setupVTK();
    }

    setupVTK() {
        // Create rendering components
        this.renderWindow = vtk.Rendering.Core.vtkRenderWindow.newInstance();
        this.renderer = vtk.Rendering.Core.vtkRenderer.newInstance();
        this.renderWindow.addRenderer(this.renderer);

        this.openGLRenderWindow = vtk.Rendering.OpenGL.vtkRenderWindow.newInstance();
        this.renderWindow.addView(this.openGLRenderWindow);

        // Create interactor
        this.interactor = vtk.Rendering.Core.vtkRenderWindowInteractor.newInstance();
        this.interactor.setView(this.openGLRenderWindow);
        this.interactor.initialize();
        this.interactor.bindEvents(this.container);

        // Setup camera
        this.renderer.resetCamera();
        const camera = this.renderer.getActiveCamera();
        camera.setPosition(5, 5, 5);
        camera.setFocalPoint(0, 0, 0);
        camera.setViewUp(0, 0, 1);

        // Set background color to black
        this.renderer.setBackground(0.0, 0.0, 0.0);

        // Add trackball camera controls
        const cameraControl = vtk.Interaction.Style.vtkInteractorStyleTrackballCamera.newInstance();
        this.interactor.setInteractorStyle(cameraControl);

        // Initial scene setup
        this.createInitialScene();
    }

    createInitialScene() {
        // Generate field points in a spherical pattern
        this.generateFieldPoints();
        
        // Create antenna geometry
        this.createAntenna();

        // Initialize field visualization
        this.createFieldVisualization();

        this.renderer.resetCamera();
        this.renderWindow.render();
    }

    generateFieldPoints() {
        const points = [];
        const numPhiPoints = 30;
        const numThetaPoints = 15;
        const numRadialPoints = 10;
        const maxRadius = 3.0;

        for (let r = 1; r <= numRadialPoints; r++) {
            const radius = (r / numRadialPoints) * maxRadius;
            for (let phi = 0; phi < numPhiPoints; phi++) {
                const phiAngle = (phi / numPhiPoints) * Math.PI * 2;
                for (let theta = 0; theta < numThetaPoints; theta++) {
                    const thetaAngle = (theta / numThetaPoints) * Math.PI;
                    const x = radius * Math.sin(thetaAngle) * Math.cos(phiAngle);
                    const y = radius * Math.sin(thetaAngle) * Math.sin(phiAngle);
                    const z = radius * Math.cos(thetaAngle);
                    points.push([x, y, z]);
                }
            }
        }
        this.fieldPoints = points;
    }

    createAntenna() {
        // Create antenna body
        const antennaHeight = 2.0;
        const antennaRadius = 0.05;
        
        const cylinder = vtk.Filters.Sources.vtkCylinderSource.newInstance({
            height: antennaHeight,
            radius: antennaRadius,
            resolution: 32,
            center: [0, 0, antennaHeight/2],
        });

        // Create base
        const base = vtk.Filters.Sources.vtkCylinderSource.newInstance({
            height: 0.2,
            radius: antennaRadius * 3,
            resolution: 32,
            center: [0, 0, 0],
        });

        // Create mapper and actor for antenna
        const antennaMapper = vtk.Rendering.Core.vtkMapper.newInstance();
        antennaMapper.setInputConnection(cylinder.getOutputPort());
        
        const baseMapper = vtk.Rendering.Core.vtkMapper.newInstance();
        baseMapper.setInputConnection(base.getOutputPort());

        // Add to renderer
        const antennaActor = vtk.Rendering.Core.vtkActor.newInstance();
        antennaActor.setMapper(antennaMapper);
        antennaActor.getProperty().setColor(0.8, 0.8, 0.8);
        antennaActor.getProperty().setSpecular(0.8);

        const baseActor = vtk.Rendering.Core.vtkActor.newInstance();
        baseActor.setMapper(baseMapper);
        baseActor.getProperty().setColor(0.7, 0.7, 0.7);

        this.renderer.addActor(antennaActor);
        this.renderer.addActor(baseActor);
    }

    createFieldVisualization() {
        // Create points for the field
        const points = vtk.Common.Core.vtkPoints.newInstance();
        this.fieldPoints.forEach(point => points.insertNextPoint(point[0], point[1], point[2]));

        // Create polydata for the field points
        const polyData = vtk.Common.DataModel.vtkPolyData.newInstance();
        polyData.setPoints(points);

        // Initialize vectors
        const numPoints = points.getNumberOfPoints();
        const vectors = new Float32Array(numPoints * 3);
        for (let i = 0; i < numPoints; i++) {
            const point = points.getPoint(i);
            const distance = Math.sqrt(point[0]**2 + point[1]**2 + point[2]**2);
            const magnitude = 1.0 / Math.max(0.5, distance);
            vectors[i*3] = point[0] * magnitude;
            vectors[i*3+1] = point[1] * magnitude;
            vectors[i*3+2] = point[2] * magnitude;
        }

        // Add vectors to polydata
        const vectorsData = vtk.Common.Core.vtkDataArray.newInstance({
            name: 'vectors',
            numberOfComponents: 3,
            values: vectors,
        });
        polyData.getPointData().setVectors(vectorsData);

        // Create arrow source for glyphs
        const arrowSource = vtk.Filters.Sources.vtkArrowSource.newInstance();
        arrowSource.setTipResolution(16);
        arrowSource.setShaftResolution(16);

        // Create glyph
        const glyph = vtk.Filters.General.vtkGlyph3D.newInstance({
            scaling: true,
            scaleMode: vtk.Filters.General.vtkGlyph3D.ScaleModes.SCALE_BY_MAGNITUDE,
            scaleArray: 'vectors',
            vectorMode: true,
            orientationArray: 'vectors',
        });
        glyph.setSourceConnection(arrowSource.getOutputPort());
        glyph.setInputData(polyData);

        // Create mapper and actor
        const mapper = vtk.Rendering.Core.vtkMapper.newInstance();
        mapper.setInputConnection(glyph.getOutputPort());
        mapper.setScalarRange(0, 1);
        mapper.setLookupTable(this.createColorMap());

        const actor = vtk.Rendering.Core.vtkActor.newInstance();
        actor.setMapper(mapper);
        actor.getProperty().setOpacity(0.8);

        this.renderer.addActor(actor);
        this.fieldActor = actor;
    }

    createColorMap() {
        const lookupTable = vtk.Rendering.Core.vtkLookupTable.newInstance();
        lookupTable.setNumberOfColors(256);
        lookupTable.setHueRange(0.667, 0.0);  // Blue to red
        lookupTable.setSaturationRange(1, 1);
        lookupTable.setValueRange(1, 1);
        lookupTable.build();
        return lookupTable;
    }

    updateField(audioAmplitude, time) {
        if (!this.fieldActor) return;

        const polyData = this.fieldActor.getMapper().getInputData();
        const points = polyData.getPoints();
        const vectors = polyData.getPointData().getVectors();
        const numPoints = points.getNumberOfPoints();
        const vectorsArray = vectors.getData();

        for (let i = 0; i < numPoints; i++) {
            const point = points.getPoint(i);
            const distance = Math.sqrt(point[0]**2 + point[1]**2 + point[2]**2);
            const phase = 2 * Math.PI * (this.frequency * time - distance);
            const magnitude = audioAmplitude / Math.max(0.5, distance);

            vectorsArray[i*3] = point[0] * magnitude * Math.sin(phase);
            vectorsArray[i*3+1] = point[1] * magnitude * Math.sin(phase);
            vectorsArray[i*3+2] = point[2] * magnitude * Math.cos(phase);
        }

        vectors.modified();
        this.renderWindow.render();
    }

    setParameters(params) {
        if (params.frequency !== undefined) {
            this.frequency = params.frequency;
        }
        // Add other parameter updates as needed
        this.renderWindow.render();
    }
}

// Initialize the visualization when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.emFieldVisualizer = new EMFieldVisualizer('interactive3d');
});