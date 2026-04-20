"""
Backup artifact builder for the OPERATE module.
Governed by: OPERATE_BASELINE_TDD.md
"""

import hashlib
import tarfile
from datetime import datetime, timezone
from pathlib import Path


def _generate_checksum(filepath: Path) -> str:
    """Generates SHA256 checksum for a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in blocks to handle large files
        for block in iter(lambda: f.read(4096), b""):
            sha256.update(block)
    return sha256.hexdigest()


def create_backup_archive(project_path: Path, slug: str, include_env: bool = False) -> tuple[bool, Path, Path, str]:
    """
    Creates a deterministic .tar.gz backup of the project path.
    By default, ignores .env files for security unless explicitly requested.
    
    Returns:
        tuple (success, archive_path, checksum_path, error_msg)
    """
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_name = f"{slug}__backup__{timestamp}.tar.gz"
        checksum_name = f"{archive_name}.sha256"
        
        # We put backups in the operate folder of the project by default, 
        # or just at the project root for now. Let's put it in `operate/backups`
        backup_dir = project_path / "operate" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        archive_path = backup_dir / archive_name
        checksum_path = backup_dir / checksum_name
        
        def _filter_tarinfo(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo | None:
            # Security boundary: do not backup the backup dir itself to avoid infinite recursion
            if "operate/backups" in tarinfo.name or "operate\\backups" in tarinfo.name:
                return None
                
            # Exclude .git and pycache
            if ".git" in tarinfo.name or "__pycache__" in tarinfo.name:
                return None
                
            # Exclude environment files unless explicitly requested
            if not include_env and ".env" in tarinfo.name and ".example" not in tarinfo.name:
                return None
                
            return tarinfo

        with tarfile.open(archive_path, "w:gz") as tar:
            # We add the contents of the project_path to the archive, but strip the absolute path
            # arcname="." means the files will be at the root of the archive
            tar.add(project_path, arcname=".", filter=_filter_tarinfo)
            
        # Verify the archive is a valid tar file
        if not tarfile.is_tarfile(archive_path):
            return False, archive_path, checksum_path, "Generated archive is corrupted."
            
        # Generate Checksum
        checksum = _generate_checksum(archive_path)
        checksum_path.write_text(f"{checksum} *{archive_name}\n")
        
        return True, archive_path, checksum_path, ""
        
    except Exception as e:
        return False, Path(""), Path(""), f"Failed to create backup archive: {e}"
