#!/usr/bin/env python3
import subprocess
import os
import argparse
import tempfile
from pathlib import Path
from solid import *
from solid.utils import *

class SolidRenderer:
    """OpenSCAD renderer using the solid library for programmatic 3D model generation"""
    
    def __init__(self):
        self.model = None
        self.segments = 50  # Default segments for smooth curves
    
    def create_cube(self, size=10, center=True):
        """Create a cube primitive"""
        return cube(size=size, center=center)
    
    def create_sphere(self, radius=5, segments=None):
        """Create a sphere primitive"""
        if segments is None:
            segments = self.segments
        return sphere(r=radius, segments=segments)
    
    def create_cylinder(self, height=10, radius=5, center=True, segments=None):
        """Create a cylinder primitive"""
        if segments is None:
            segments = self.segments
        return cylinder(h=height, r=radius, center=center, segments=segments)
    
    def create_cone(self, height=10, r1=5, r2=0, center=True, segments=None):
        """Create a cone primitive"""
        if segments is None:
            segments = self.segments
        return cylinder(h=height, r1=r1, r2=r2, center=center, segments=segments)
    
    def union(self, *objects):
        """Create a union of multiple objects"""
        return union()(*objects)
    
    def difference(self, base, *subtract_objects):
        """Subtract objects from base object"""
        return difference()(base, *subtract_objects)
    
    def intersection(self, *objects):
        """Create intersection of multiple objects"""
        return intersection()(*objects)
    
    def translate(self, vector, obj):
        """Translate an object by a vector [x, y, z]"""
        return translate(vector)(obj)
    
    def rotate(self, angles, obj):
        """Rotate an object by angles [x, y, z] in degrees"""
        return rotate(angles)(obj)
    
    def scale(self, factors, obj):
        """Scale an object by factors [x, y, z]"""
        return scale(factors)(obj)
    
    def color(self, color_name, obj):
        """Apply color to an object"""
        return color(color_name)(obj)
    
    def render_to_scad(self, model, filename=None):
        """Render solid model to OpenSCAD code"""
        if filename:
            return scad_render_to_file(model, filename)
        else:
            return scad_render(model)
    
    def render_to_images(self, model, output_dir=".", base_name="solid_render"):
        """Render solid model to images in multiple views"""
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Generate OpenSCAD code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.scad', delete=False) as f:
            scad_code = self.render_to_scad(model)
            f.write(scad_code)
            temp_scad_file = f.name
        
        try:
            # Camera format: eye_x,y,z,center_x,y,z
            views = {
                'top': ('0,0,100,0,0,0', 'ortho'),         # Looking down from above
                'front': ('0,-100,0,0,0,0', 'ortho'),      # Looking from front
                'left': ('-100,0,0,0,0,0', 'ortho'),       # Looking from left side
                '3d': ('70,70,50,0,0,0', 'perspective')    # Isometric view
            }
            
            success = True
            for view_name, (camera, projection) in views.items():
                output_file = output_dir / f"{base_name}_{view_name}.png"
                cmd = [
                    'openscad',
                    '-o', str(output_file),
                    '--autocenter',
                    '--viewall',
                    '--imgsize=800,600',
                    '--camera', camera,
                    '--projection', projection,
                    temp_scad_file
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Error rendering {view_name}: {result.stderr}")
                    success = False
                else:
                    print(f"Rendered: {output_file}")
            
            return success
        finally:
            os.unlink(temp_scad_file)


def example_complex_model():
    """Create a complex model demonstrating various solid operations"""
    renderer = SolidRenderer()
    
    # Create a hollowed cube with sphere cutouts
    outer_cube = renderer.create_cube(size=20, center=True)
    inner_sphere = renderer.create_sphere(radius=13, segments=100)
    
    # Create corner cutouts
    corner_spheres = []
    for x in [-10, 10]:
        for y in [-10, 10]:
            for z in [-10, 10]:
                sphere = renderer.create_sphere(radius=5, segments=50)
                sphere = renderer.translate([x, y, z], sphere)
                corner_spheres.append(sphere)
    
    # Combine all cutouts
    all_cutouts = renderer.union(inner_sphere, *corner_spheres)
    
    # Create the final model
    model = renderer.difference(outer_cube, all_cutouts)
    
    # Add some decorative elements
    ring = renderer.difference(
        renderer.create_cylinder(height=5, radius=15, center=True),
        renderer.create_cylinder(height=6, radius=12, center=True)
    )
    ring = renderer.rotate([90, 0, 0], ring)
    
    # Color the components
    model = renderer.color('lightblue', model)
    ring = renderer.color('gold', ring)
    
    # Combine final model
    final_model = renderer.union(model, ring)
    
    return final_model


def example_parametric_gear():
    """Create a simple parametric gear-like object"""
    renderer = SolidRenderer()
    
    # Base cylinder
    base = renderer.create_cylinder(height=10, radius=20, center=True)
    
    # Create teeth
    teeth = []
    num_teeth = 12
    for i in range(num_teeth):
        angle = i * 360 / num_teeth
        tooth = renderer.create_cube(size=[8, 4, 10], center=True)
        tooth = renderer.translate([20, 0, 0], tooth)
        tooth = renderer.rotate([0, 0, angle], tooth)
        teeth.append(tooth)
    
    # Center hole
    hole = renderer.create_cylinder(height=11, radius=5, center=True)
    
    # Combine
    gear = renderer.union(base, *teeth)
    gear = renderer.difference(gear, hole)
    gear = renderer.color('darkgreen', gear)
    
    return gear


def main():
    parser = argparse.ArgumentParser(description='Render 3D models using solid library')
    parser.add_argument('--example', choices=['complex', 'gear'], 
                        help='Render a built-in example model')
    parser.add_argument('-o', '--output-dir', default='.', 
                        help='Output directory for images (default: current directory)')
    parser.add_argument('-n', '--name', default='solid_render',
                        help='Base name for output files (default: solid_render)')
    
    args = parser.parse_args()
    
    renderer = SolidRenderer()
    
    if args.example == 'complex':
        model = example_complex_model()
        print("Creating complex model with hollowed cube and decorative ring...")
    elif args.example == 'gear':
        model = example_parametric_gear()
        print("Creating parametric gear model...")
    else:
        # Default simple example
        print("Creating default example: cube with sphere cutout...")
        cube = renderer.create_cube(size=10, center=True)
        sphere = renderer.create_sphere(radius=6.5, segments=100)
        model = renderer.difference(cube, sphere)
        model = renderer.color('orange', model)
    
    print(f"Rendering views to '{args.output_dir}'...")
    if renderer.render_to_images(model, args.output_dir, args.name):
        print(f"Successfully rendered 4 views:")
        print(f"  - {args.name}_top.png")
        print(f"  - {args.name}_front.png")
        print(f"  - {args.name}_left.png")
        print(f"  - {args.name}_3d.png")
        return 0
    else:
        print("Some views failed to render")
        return 1


if __name__ == "__main__":
    exit(main())