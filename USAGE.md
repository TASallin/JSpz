# JSpz - SPZ to glTF Conversion Tool

This tool converts SPZ (Gaussian splat) files to glTF format for use with Cesium.

## Prerequisites

- Java 8 or higher (JDK required)
- Apache Maven 3.6 or higher
- Python 3.6+ (for the Python wrapper)
- **JAVA_HOME environment variable must be set**

## Quick Start with Python Wrapper (Recommended)

The easiest way to use this tool is with the included Python wrapper that provides both GUI and command-line interfaces.

### Setup

1. **Build the project** (one-time setup):
   ```bash
   mvn clean install
   ```

2. **Set JAVA_HOME** (if not already set):
   - **Windows**: Set environment variable `JAVA_HOME` to your JDK path (e.g., `C:\Program Files\Java\jdk-17`)
   - **Linux/Mac**: Add `export JAVA_HOME=/path/to/jdk` to your shell profile

### GUI Mode (Easy for beginners)

Launch the graphical interface:

```bash
python spz_converter.py --gui
```

1. Click "Browse" to select your SPZ file
2. Click "Browse" to select output directory  
3. Optionally change the content filename (default: `content.glb`)
4. Click "Convert"
5. Monitor progress in the log area

### Command Line Mode

Convert files directly from the command line:

```bash
# Basic usage
python spz_converter.py input.spz output_directory/

# With custom content filename
python spz_converter.py input.spz output_directory/ --content-name my_model.glb

# Help
python spz_converter.py --help
```

**Examples:**
```bash
# Convert winter_garden_residence.spz to ./output/ directory
python spz_converter.py ./data/winter_garden_residence.spz ./output/

# Convert with custom GLB filename
python spz_converter.py ./data/my_model.spz ./cesium_assets/ --content-name gaussian_splats.glb
```

## Advanced Usage (Direct Java/Maven)

For advanced users who want to use Maven directly:

### Command Line with Arguments

The Java tool now accepts command-line arguments:

```bash
mvn exec:java -Dexec.mainClass="de.javagl.jspz.examples.SpzToTileset" \
  -Dexec.args="input.spz output_directory/ content.glb" \
  -pl jspz-main
```

### Legacy Method (Deprecated)

The old method of editing the Java file still works but is not recommended:

1. Edit `jspz-main/src/main/java/de/javagl/jspz/examples/SpzToTileset.java`
2. Modify the hardcoded paths in the `main` method
3. Run: `mvn exec:java -Dexec.mainClass="de.javagl.jspz.examples.SpzToTileset" -pl jspz-main`

## Output Files

The conversion creates two files in your specified output directory:
- `tileset.json` - 3D Tiles tileset definition
- `content.glb` (or your custom name) - Binary glTF file with compressed Gaussian splats

## Using the Output in Cesium

The generated files can be loaded in CesiumJS:

```javascript
const tileset = viewer.scene.primitives.add(new Cesium.Cesium3DTileset({
    url: 'path/to/your/tileset.json'
}));
```

## Troubleshooting

### Common Issues

- **"JAVA_HOME environment variable is not set"**
  - Set JAVA_HOME to your JDK installation directory
  - Restart your terminal/command prompt after setting

- **"Maven not found in PATH"**
  - Install Apache Maven and add it to your system PATH
  - On Windows, use `mvn.cmd` instead of `mvn` if needed

- **Build fails**
  - Ensure Java 8+ JDK (not just JRE) and Maven are installed
  - Run `mvn clean install` from the root directory first
  - Check that JAVA_HOME points to a JDK, not JRE

- **Python wrapper fails**
  - Ensure Python 3.6+ is installed
  - Install tkinter if using GUI mode: `pip install tk` (usually included with Python)
  - Check that the Java project builds successfully first

- **Conversion fails**
  - Verify your SPZ file is valid and not corrupted
  - Check file permissions on input and output directories
  - Look at the detailed error messages in the log

## Coordinate Systems

The tool automatically converts from SPZ coordinate system (RUB) to glTF coordinate system (LUF) for proper display in Cesium.