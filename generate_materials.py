#!/usr/bin/env python3
"""
Material Generator for Repak
This script generates material files for repak based on a list of material names.
"""

import json
import os
import shutil
from pathlib import Path


def create_material_json(material_name):
    """Create a material JSON file based on the template."""
    template = {
        "name": material_name,
        "width": 2048,
        "height": 2048,
        "depth": 0,
        "glueFlags": "0x56000420",
        "glueFlags2": "0x0",
        "blendStates": [
            "0xF0000000",
            "0xF0000000",
            "0xF0000000",
            "0xF0000000",
            "0xF0000000",
            "0xF0000000",
            "0xF0000000",
            "0xF0000000"
        ],
        "blendStateMask": "0x4",
        "depthStencilFlags": "0x17",
        "rasterizerFlags": "0x6",
        "uberBufferFlags": "0x0",
        "features": "0x1F5A92BD",
        "samplers": "0x1D0300",
        "surfaceProp": "default",
        "surfaceProp2": "",
        "shaderType": "sknp",
        "shaderSet": "0x97E4F7D956E5E6CE",
        "$textures": {
            "0": f"texture/{material_name}_0.rpak",
            "1": f"texture/{material_name}_1.rpak",
            "2": f"texture/{material_name}_2.rpak",
            "3": f"texture/{material_name}_3.rpak",
            "4": f"texture/{material_name}_4.rpak",
            "5": f"texture/{material_name}_5.rpak",
            "6": f"texture/{material_name}_6.rpak"
        },
        "$depthShadowMaterial": "0x2B93C99C67CC8B51",
        "$depthPrepassMaterial": "0x1EBD063EA03180C7",
        "$depthVSMMaterial": "0xF95A7FA9E8DE1A0E",
        "$depthShadowTightMaterial": "0x227C27B608B3646B",
        "$colpassMaterial": "0x0",
        "$textureAnimation": "0x0"
    }
    return template


def update_common_flowstate_json(material_paths):
    """Update common_flowstate.json with new material entries."""
    json_file = "common_flowstate.json"
    
    # Read the file as text to handle potential JSON issues
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {json_file} not found")
        return
    
    # Check which material paths already exist
    new_material_paths = []
    existing_paths = []
    
    for material_path in material_paths:
        # Check if this path already exists in the file
        if f'"{material_path}"' in content:
            existing_paths.append(material_path)
            print(f"  Skipping (already exists): {material_path}")
        else:
            new_material_paths.append(material_path)
    
    if not new_material_paths:
        print("All material paths already exist in common_flowstate.json. No changes made.")
        return
    
    # Find the first "_type": "matl" entry
    first_matl_pattern = '"_type": "matl"'
    first_matl_index = content.find(first_matl_pattern)
    
    if first_matl_index == -1:
        print("Warning: No existing material entries found in common_flowstate.json")
        return
    
    # Find the start of this entry (look for the opening brace before it)
    entry_start = content.rfind('{', 0, first_matl_index)
    if entry_start == -1:
        print("Error: Could not find the start of the first material entry")
        return
    
    # Create new material entries as text (only for new paths)
    new_entries_text = ""
    for material_path in new_material_paths:
        new_entries_text += f'''    {{
      "_type": "matl",
      "_path": "{material_path}"
    }},
'''
    
    # Insert new entries before the first material entry
    new_content = content[:entry_start] + new_entries_text + content[entry_start:]
    
    # Write back to the JSON file
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Added {len(new_material_paths)} new material entries to common_flowstate.json")
        if existing_paths:
            print(f"Skipped {len(existing_paths)} existing entries")
    except Exception as e:
        print(f"Error writing to {json_file}: {e}")
        return


def generate_materials(material_names):
    """Generate materials for the given list of material names."""
    if not material_names:
        print("No material names provided.")
        return
    
    # Check if testuber.uber exists
    uber_template = "testuber.uber"
    if not os.path.exists(uber_template):
        print(f"Error: {uber_template} not found in the current directory.")
        return
    
    assets_dir = Path("assets")
    material_paths = []
    
    for material_name in material_names:
        print(f"Processing material: {material_name}")
        
        # Get the base name (last part of the path)
        base_name = material_name.split('/')[-1]
        
        # Add _sknp.rpak suffix to the base name
        material_file = f"{base_name}_sknp.rpak"
        
        # Create the material path (no individual subfolder)
        material_path = f"material/{material_name}_sknp.rpak"
        material_paths.append(material_path)
        
        # Create directory structure (parent folder only)
        parent_path = '/'.join(material_name.split('/')[:-1]) if '/' in material_name else ''
        if parent_path:
            material_dir = assets_dir / "material" / parent_path.replace('/', os.sep)
        else:
            material_dir = assets_dir / "material"
        material_dir.mkdir(parents=True, exist_ok=True)
        
        # Create JSON file
        json_content = create_material_json(material_name)
        json_file_path = material_dir / f"{base_name}_sknp.json"
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, indent=4)
        
        # Copy uber file
        uber_file_path = material_dir / f"{base_name}_sknp.uber"
        shutil.copy2(uber_template, uber_file_path)
        
        print(f"  Created: {json_file_path}")
        print(f"  Created: {uber_file_path}")
    
    # Update common_flowstate.json
    print("\nUpdating common_flowstate.json...")
    update_common_flowstate_json(material_paths)
    
    print(f"\nCompleted processing {len(material_names)} materials.")


def main():
    """Main function to get input and process materials."""
    print("Material Generator for Repak")
    print("=" * 40)
    
    # Get material names from user input
    print("Enter material names (one per line, empty line to finish):")
    material_names = []
    
    while True:
        material_name = input().strip()
        if not material_name:
            break
        material_names.append(material_name)
    
    if not material_names:
        print("No material names provided. Exiting.")
        return
    
    print(f"\nMaterial names to process:")
    for i, name in enumerate(material_names, 1):
        print(f"  {i}. {name}")
    
    confirm = input("\nProceed with generation? (y/N): ").strip().lower()
    if confirm in ('y', 'yes'):
        generate_materials(material_names)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
