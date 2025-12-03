&nbsp;Kiro: Automated Screenshot Organizer



> "I hate sorting screenshots manually, so I built Kiro."



Kiro is a lightweight, background automation tool written in Python. It watches your Desktop for new screenshots and instantly classifies, renames, and moves them into month-wise folders (e.g., `Documents/Kiro\_Archive/Screenshots/2025-05`).



\##  Features

\- Zero-Click Automation:\*\* Runs in the background using `watchdog`.

\- Smart Classification:\*\* Detects screenshot keywords in multiple languages (English, Japanese, Chinese, etc.).

\-  OneDrive Compatible:\*\* Automatically detects if your Desktop is redirected to OneDrive (common on Windows 11).

\-  Collision Safety:\*\* Never overwrites files. If `Screenshot.png` exists, it renames the new one with a precise timestamp.

\-  Rich UI:\*\* Beautiful CLI output with progress bars and status indicators (when running manually).



\##  Installation



1\. Clone the repository:

&nbsp;  ```bash

&nbsp;  git clone \[https://github.com/YOUR\_USERNAME/kiro-organizer.git](https://github.com/YOUR\_USERNAME/kiro-organizer.git)

&nbsp;  cd kiro-organizer

