#!/usr/bin/env python3
"""
------------------------------------------------------------------------
  KIRO: The Automated Screenshot Organizer
  "I hate sorting screenshots, so I let Kiro do it."
------------------------------------------------------------------------
"""

import os
import sys
import shutil
import time
import argparse
import platform
from datetime import datetime
from pathlib import Path

# --- Configuration (Smart Auto-Detection) ---
def get_desktop_path():
    """Finds the real Desktop, checking OneDrive first."""
    # 1. Check OneDrive Desktop (Standard on modern Windows)
    onedrive = Path.home() / "OneDrive" / "Desktop"
    if onedrive.exists():
        return onedrive
    # 2. Check Standard Desktop
    return Path.home() / "Desktop"

DEFAULT_SOURCE = get_desktop_path()
DEFAULT_TARGET = Path.home() / "Documents" / "Kiro_Archive"

# Supported formats
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp', '.heic', '.tiff'}

# Keywords to identify screenshots across languages
SCREENSHOT_KEYWORDS = [
    'screenshot', 'screen_shot', 'screen-shot', 'screen shot', 
    'スクリーンショット', '截屏', '屏幕快照', 'captura', 'bildschirmfoto'
]

# Try to import Rich for beautiful output, otherwise fallback to standard
try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.progress import track
    custom_theme = Theme({"info": "cyan", "warning": "yellow", "error": "bold red", "success": "bold green"})
    console = Console(theme=custom_theme)
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    class Console:
        def print(self, text, style=None): print(text)
    console = Console()

class KiroOrganizer:
    def __init__(self, source: Path, target: Path, dry_run: bool = False):
        self.source = source
        self.target = target
        self.dry_run = dry_run
        self.stats = {"moved": 0, "errors": 0}

    def _is_screenshot(self, filename: str) -> bool:
        """Determines if a file is a screenshot based on keywords."""
        ln = filename.lower()
        return any(kw in ln for kw in SCREENSHOT_KEYWORDS)

    def _get_creation_date(self, path: Path) -> datetime:
        """Robust cross-platform creation date retrieval."""
        stat = path.stat()
        timestamp = stat.st_mtime # Default fallback
        
        try:
            if platform.system() == 'Windows':
                timestamp = stat.st_ctime
            elif hasattr(stat, 'st_birthtime'): # macOS / BSD
                timestamp = stat.st_birthtime
            else:
                # Linux often doesn't give birthtime, use mtime
                timestamp = stat.st_mtime
        except AttributeError:
            pass
            
        return datetime.fromtimestamp(timestamp)

    def _get_unique_path(self, folder: Path, filename: str) -> Path:
        """Handles filename collisions by appending a timestamp."""
        destination = folder / filename
        if not destination.exists():
            return destination
        
        # Collision detected
        src_path = Path(filename)
        stem = src_path.stem
        suffix = src_path.suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return folder / f"{stem}_{timestamp}{suffix}"

    def process_file(self, file_path: Path) -> bool:
        """Moves a single file to the correct month folder."""
        try:
            if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_EXTS:
                return False

            if not self._is_screenshot(file_path.name):
                return False

            # Calculate destination
            creation_date = self._get_creation_date(file_path)
            month_folder = creation_date.strftime("%Y-%m")
            target_dir = self.target / "Screenshots" / month_folder
            
            dest_path = self._get_unique_path(target_dir, file_path.name)

            if self.dry_run:
                console.print(f"[warning][DRY-RUN][/] Would move: {file_path.name} -> {month_folder}")
                return True

            # Create dir and move
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(dest_path))
            
            console.print(f"[success]✔ Moved:[/success] {file_path.name} -> [info]{month_folder}[/info]")
            self.stats["moved"] += 1
            return True

        except Exception as e:
            console.print(f"[error]Error processing {file_path.name}: {e}[/error]")
            self.stats["errors"] += 1
            return False

    def run_scan(self):
        """One-time scan of the folder."""
        if not self.source.exists():
            console.print(f"[error]Source directory {self.source} does not exist.[/error]")
            return

        files = [f for f in self.source.iterdir() if f.is_file()]
        
        console.print(f"[bold]Kiro is organizing {len(files)} files from:[/bold] {self.source}")
        
        # Use rich progress bar if available
        iterator = track(files, description="Sorting...") if HAS_RICH else files
        
        for entry in iterator:
            self.process_file(entry)

        console.print("------------------------------------------------")
        console.print(f"[bold green]Done.[/] Moved: {self.stats['moved']} | Errors: {self.stats['errors']}")

    def run_watch(self):
        """Watchdog mode."""
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            console.print("[error]Watch mode requires 'watchdog'. Install via: pip install watchdog[/error]")
            return

        handler = self

        class Watcher(FileSystemEventHandler):
            def on_created(self, event):
                if event.is_directory: return
                # Debounce: wait slightly for file write to complete
                time.sleep(1.0) 
                handler.process_file(Path(event.src_path))

        observer = Observer()
        observer.schedule(Watcher(), str(self.source), recursive=False)
        observer.start()
        
        console.print(f"[bold cyan]Kiro Watcher Active[/bold cyan]")
        console.print(f"Watching: {self.source}")
        console.print(f"Target:   {self.target}")
        console.print("Press [bold red]Ctrl+C[/] to stop.")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

def main():
    parser = argparse.ArgumentParser(description="Kiro: Automated Screenshot Organizer")
    parser.add_argument("--source", "-s", type=str, default=str(DEFAULT_SOURCE), help="Folder to watch")
    parser.add_argument("--target", "-t", type=str, default=str(DEFAULT_TARGET), help="Folder to store sorted images")
    parser.add_argument("--watch", "-w", action="store_true", help="Run in background watch mode")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without moving files")
    
    args = parser.parse_args()
    
    organizer = KiroOrganizer(
        source=Path(args.source), 
        target=Path(args.target), 
        dry_run=args.dry_run
    )

    if args.watch:
        organizer.run_watch()
    else:
        organizer.run_scan()

if __name__ == "__main__":
    main()