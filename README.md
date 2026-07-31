# FloydMusic

FloydMusic is a lightweight Discord music bot written in Python. It joins a voice channel and plays audio from a URL, a search query, or a directly uploaded audio file, with a simple queue system and per-server volume control.

## Features

- Play audio from a URL (YouTube and other sites supported by `yt-dlp`) or from an uploaded audio attachment
- Queue system, so multiple tracks can be added and played in order
- Adjustable volume, starting at 1 with no upper limit
- Simple prefix commands, no slash commands

## Requirements

- **Python 3.10 or newer**
- **FFmpeg** installed and available on the system PATH
- The Python packages listed in `requirements.txt`

## Installing Python

1. Download the installer from [python.org/downloads](https://www.python.org/downloads/).
2. Run the installer and make sure to check **"Add python.exe to PATH"** before clicking Install.
3. Confirm the installation by opening a terminal and running:
   ```
   py --version
   ```

## Installing FFmpeg

### Windows

1. Go to [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) and download the **release-essentials** build.
2. Extract the downloaded ZIP file to a permanent location, for example `C:\ffmpeg`.
3. Open the extracted folder and locate the `bin` subfolder, which contains `ffmpeg.exe`.
4. Add that `bin` folder to your system PATH:
   - Open **Control Panel > System > Advanced system settings**.
   - Click **Environment Variables**.
   - Under **System variables**, select **Path** and click **Edit**.
   - Click **New** and paste the full path to the `bin` folder, e.g. `C:\ffmpeg\bin`.
   - Click OK on every window to save.
5. Open a new terminal window and confirm it worked:
   ```
   ffmpeg -version
   ```

### macOS

Using Homebrew:
```
brew install ffmpeg
```

### Linux (Debian/Ubuntu)

```
sudo apt update
sudo apt install ffmpeg
```

## Installation

1. Clone or download this repository.
2. Install the dependencies:
   ```
   py -m pip install -r requirements.txt
   ```
3. Open `bot.py` and replace `PUT_YOUR_TOKEN_HERE` with your bot's token, available at [discord.com/developers/applications](https://discord.com/developers/applications) under your application's **Bot** tab.
4. Enable the **Message Content Intent** for your bot in the same Bot tab, under Privileged Gateway Intents.
5. Run the bot:
   ```
   py bot.py
   ```

## Commands

All commands use the `.` prefix.

| Command | Description |
|---|---|
| `.join` | Joins the voice channel of the user who called it |
| `.leave` | Leaves the voice channel and clears the queue |
| `.play <url, search, or attachment>` | Adds a track to the queue and starts playing if idle |
| `.stop` | Stops playback and clears the entire queue |
| `.volume <number>` | Sets the playback volume, starting at 1 with no upper limit |
| `.help` | Shows the list of available commands |

## Notes

- Each server (guild) has its own independent queue and volume setting.
- If no FFmpeg installation is found on the system PATH, playback will fail even if the bot connects to voice successfully.
