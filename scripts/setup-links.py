#!/usr/bin/env python3
"""
Cross-platform symlink/directory setup script for AI Agent Sandbox.
Creates necessary directory links that work on Windows, Linux, macOS, and Termux.
"""

import os
import sys
import shutil
from pathlib import Path

def create_cross_platform_link(source: Path, target: Path) -> bool:
    """
    Create a directory link that works across platforms.
    On Unix-like systems: creates symlink
    On Windows: creates junction or copies directory if junction fails
    """
    try:
        # Remove target if it exists
        if target.exists():
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

        # Try platform-specific linking
        if os.name == 'nt':  # Windows
            try:
                # Try creating a junction first (requires admin privileges)
                import subprocess
                subprocess.run([
                    'mklink', '/J', str(target), str(source)
                ], shell=True, check=True, capture_output=True)
                print(f"✅ Created Windows junction: {target} -> {source}")
                return True
            except subprocess.CalledProcessError:
                # Fall back to directory copy for Windows
                print(f"⚠️  Junction failed, copying directory: {target}")
                shutil.copytree(source, target)
                print(f"✅ Copied directory: {target} <- {source}")
                return True
        else:  # Unix-like systems (Linux, macOS, Termux)
            target.symlink_to(source, target_is_directory=True)
            print(f"✅ Created symlink: {target} -> {source}")
            return True

    except Exception as e:
        print(f"❌ Failed to create link: {target} -> {source}")
        print(f"   Error: {e}")
        return False

def setup_project_links():
    """Set up all necessary directory links for the project."""
    project_root = Path(__file__).parent.parent

    print("🔗 Setting up cross-platform directory links...")
    print(f"📁 Project root: {project_root}")

    links_to_create = [
        # tools -> tool_implementations
        (project_root / "tool_implementations", project_root / "tools"),
    ]

    success_count = 0
    total_count = len(links_to_create)

    for source, target in links_to_create:
        if source.exists():
            if create_cross_platform_link(source, target):
                success_count += 1
        else:
            print(f"⚠️  Source directory not found: {source}")

    print(f"\n📊 Link setup complete: {success_count}/{total_count} successful")

    if success_count == total_count:
        print("🎉 All directory links created successfully!")
        return True
    else:
        print("⚠️  Some links failed to create. Check the output above.")
        return False

def verify_links():
    """Verify that all required links exist and are accessible."""
    project_root = Path(__file__).parent.parent

    required_links = [
        (project_root / "tools", project_root / "tool_implementations"),
    ]

    print("\n🔍 Verifying directory links...")

    all_valid = True
    for link_path, expected_target in required_links:
        if not link_path.exists():
            print(f"❌ Missing link: {link_path}")
            all_valid = False
            continue

        # Check if it's a valid link/directory
        if link_path.is_dir():
            # Try to access a known file in the target
            test_file = link_path / "index.js"
            if test_file.exists():
                print(f"✅ Valid link: {link_path}")
            else:
                print(f"❌ Invalid link (missing expected content): {link_path}")
                all_valid = False
        else:
            print(f"❌ Not a directory: {link_path}")
            all_valid = False

    if all_valid:
        print("🎉 All directory links are valid!")
    else:
        print("⚠️  Some directory links are invalid.")

    return all_valid

def main():
    """Main setup function."""
    print("🚀 AI Agent Sandbox - Cross-Platform Link Setup")
    print("=" * 50)

    # Setup links
    setup_success = setup_project_links()

    # Verify links
    verify_success = verify_links()

    print("\n" + "=" * 50)

    if setup_success and verify_success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python validate.py' to check configuration")
        print("2. Run 'npm test' to verify the server works")
        print("3. Start developing with your AI agents!")
        return 0
    else:
        print("❌ Setup completed with issues.")
        print("Please check the output above and fix any problems.")
        return 1

if __name__ == "__main__":
    sys.exit(main())