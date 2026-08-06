import os
import zipfile
from pathlib import Path

def compile_archive():
    project_root = Path(__file__).resolve().parent.parent.parent
    zip_path = project_root / "policy-intelligence-system.zip"
    
    print(f"Compiling clean delivery package...")
    print(f"Root: {project_root}")
    print(f"Target: {zip_path}")
    
    exclude_dirs = {
        ".git",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        ".idea",
        "scratch"
    }
    
    exclude_files = {
        "policy-intelligence-system.zip",
        "policy-intelligence-system-clean.zip",
        "policyiq.zip",
        "user_manual.md",
        "user_manual.pdf",
        "design.md",
        "policyoraauditreport.docx",
        "~$licyoraauditreport.docx",
        ".ds_store",
        "thumbs.db"
    }

    # Remove existing zip if present
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_root):
            path_parts = Path(root).relative_to(project_root).parts
            
            # Skip excluded directories
            if any(part in exclude_dirs for part in path_parts):
                continue
                
            # Filter out subdirectories in-place to avoid descending into them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.lower() in exclude_files:
                    continue
                    
                file_path = Path(root) / file
                # Skip massive binary log files or local DB copies
                if file_path.suffix in ['.db', '.sqlite', '.sqlite3', '.pyc']:
                    continue
                    
                relative_path = file_path.relative_to(project_root)
                archive_name = Path("policy-intelligence-system") / relative_path
                
                zipf.write(file_path, arcname=str(archive_name))
                
    print(f"[SUCCESS] Re-compiled delivery package. Size: {zip_path.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    compile_archive()
