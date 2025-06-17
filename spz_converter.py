#!/usr/bin/env python3
"""
SPZ to glTF Converter - Python wrapper for the Java SPZ conversion tool.
Supports both command-line and GUI interfaces.
"""

import argparse
import os
import subprocess
import sys
import shutil
from pathlib import Path
from typing import Optional, Tuple

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class SPZConverter:
    """Main converter class that handles the Java tool execution."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.java_main_class = "de.javagl.jspz.examples.SpzToTileset"
        self.maven_module = "jspz-main"
    
    def check_prerequisites(self) -> Tuple[bool, str]:
        """
        Check if Maven and Java are properly installed and configured.
        
        Returns:
            Tuple of (success, error_message)
        """
        # Check if Maven is available
        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"
        if not shutil.which(mvn_cmd):
            return False, "Maven not found in PATH. Please install Maven and add it to PATH."
        
        # Check if JAVA_HOME is set
        java_home = os.environ.get("JAVA_HOME")
        if not java_home:
            return False, "JAVA_HOME environment variable is not set. Please set JAVA_HOME to your JDK installation."
        
        # Check if Java is available
        java_exe = Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java")
        if not java_exe.exists():
            return False, f"Java executable not found at {java_exe}. Please check JAVA_HOME setting."
        
        # Test Maven with a simple command
        try:
            result = subprocess.run([mvn_cmd, "--version"], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                return False, f"Maven test failed: {result.stderr}"
        except Exception as e:
            return False, f"Maven test failed: {e}"
        
        return True, ""
    
    def convert(self, input_file: str, output_dir: str, content_filename: str = "content.glb") -> bool:
        """
        Convert SPZ file to glTF tileset.
        
        Args:
            input_file: Path to input SPZ file
            output_dir: Output directory for generated files
            content_filename: Name for the GLB content file
            
        Returns:
            True if conversion succeeded, False otherwise
        """
        # Check prerequisites first
        prereq_ok, prereq_error = self.check_prerequisites()
        if not prereq_ok:
            print(f"✗ Prerequisites check failed: {prereq_error}")
            return False
        
        # Validate inputs
        if not Path(input_file).exists():
            print(f"✗ Input file '{input_file}' does not exist")
            return False
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Use correct Maven command for Windows/Unix
        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"
        
        # Convert paths to absolute paths and handle Windows paths properly
        abs_input = str(Path(input_file).resolve())
        abs_output = str(Path(output_dir).resolve())
        
        # Build Maven command
        cmd = [
            mvn_cmd, "exec:java",
            f"-Dexec.mainClass={self.java_main_class}",
            f"-Dexec.args={abs_input} {abs_output} {content_filename}",
            "-pl", self.maven_module,
            "-q"  # Quiet mode
        ]
        
        try:
            print(f"Converting {input_file} to {output_dir}...")
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✓ Conversion completed successfully!")
                print(f"  Output files:")
                print(f"    - {Path(output_dir) / 'tileset.json'}")
                print(f"    - {Path(output_dir) / content_filename}")
                return True
            else:
                print(f"✗ Conversion failed!")
                print(f"Return code: {result.returncode}")
                if result.stdout:
                    print(f"Standard output: {result.stdout}")
                if result.stderr:
                    print(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Conversion timed out after 5 minutes")
            return False
        except FileNotFoundError as e:
            print(f"✗ Command not found: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False


class SPZConverterGUI:
    """GUI interface for the SPZ converter."""
    
    def __init__(self):
        self.converter = SPZConverter()
        self.root = tk.Tk()
        self.root.title("SPZ to glTF Converter")
        self.root.geometry("600x400")
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.content_filename = tk.StringVar(value="content.glb")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file selection
        ttk.Label(main_frame, text="Input SPZ File:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(input_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=1, padx=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        # Output directory selection
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1, padx=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        # Content filename
        ttk.Label(main_frame, text="Content Filename:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(main_frame, textvariable=self.content_filename, width=30).grid(row=5, column=0, sticky=tk.W, pady=(0, 20))
        
        # Convert button
        ttk.Button(main_frame, text="Convert", command=self.convert).grid(row=6, column=0, pady=(0, 20))
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def browse_input_file(self):
        """Browse for input SPZ file."""
        filename = filedialog.askopenfilename(
            title="Select SPZ file",
            filetypes=[("SPZ files", "*.spz"), ("All files", "*.*")]
        )
        if filename:
            self.input_file.set(filename)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select output directory")
        if dirname:
            self.output_dir.set(dirname)
    
    def log(self, message: str):
        """Add message to log area."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def convert(self):
        """Run the conversion."""
        input_file = self.input_file.get().strip()
        output_dir = self.output_dir.get().strip()
        content_filename = self.content_filename.get().strip()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input SPZ file")
            return
        
        if not output_dir:
            messagebox.showerror("Error", "Please select an output directory")
            return
        
        if not content_filename:
            content_filename = "content.glb"
            self.content_filename.set(content_filename)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Redirect print to log
        import io
        import contextlib
        
        log_stream = io.StringIO()
        with contextlib.redirect_stdout(log_stream):
            success = self.converter.convert(input_file, output_dir, content_filename)
        
        # Display log output
        self.log(log_stream.getvalue())
        
        if success:
            messagebox.showinfo("Success", "Conversion completed successfully!")
        else:
            messagebox.showerror("Error", "Conversion failed. Check the log for details.")
    
    def run(self):
        """Start the GUI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Convert SPZ files to glTF tilesets for Cesium")
    parser.add_argument("--gui", action="store_true", help="Launch GUI interface")
    parser.add_argument("input_file", nargs="?", help="Input SPZ file")
    parser.add_argument("output_dir", nargs="?", help="Output directory")
    parser.add_argument("--content-name", default="content.glb", 
                       help="Name for the GLB content file (default: content.glb)")
    parser.add_argument("--project-root", help="Path to the Java project root directory")
    
    args = parser.parse_args()
    
    # GUI mode
    if args.gui:
        if not GUI_AVAILABLE:
            print("Error: GUI not available. Please install tkinter.")
            sys.exit(1)
        
        gui = SPZConverterGUI()
        gui.run()
        return
    
    # CLI mode
    if not args.input_file or not args.output_dir:
        parser.print_help()
        sys.exit(1)
    
    converter = SPZConverter(args.project_root)
    success = converter.convert(args.input_file, args.output_dir, args.content_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()