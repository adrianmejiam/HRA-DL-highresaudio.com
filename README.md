# HRA-DL
Tool written in Python to download streamable FLACs from highresaudio.com.

**This is the initial version, so the following are NOT implemented yet:**
- CLI support    
- tagging customization   

[Pre-compiled binaries.](https://github.com/Sorrow446/HRA-DL-highresaudio.com/releases)

![](https://thoas.feralhosting.com/sorrow/HRA-DL/b1.jpg)

# Setup
## Mandatory ##
The following field values need to be inputted into the config file:
- email
- password - in plain text
There's no quality field because the API only returns the highest available quality FLAC.

**You can't download ANY tracks with a free account.**

# Update Log #
### 2nd Aug 19 - Release 1 ###

# Misc Info
- Written around Python v3.6.7.      
- If there's a booklet available, it'll be fetched.    
- Any special characters that your OS doesn't support in filenames will be replaced with "-".    
- Filename clashes will be handled inside of album folders. If a clash occurs inside an album folder, the previous file will be deleted.     
If you need to get in touch: Sorrow#5631, [Reddit](https://www.reddit.com/user/Sorrow446)

# Disclaimer
I will not be responsible for how you use HRA-DL.    
HIGHRESAUDIO brand and name is the registered trademark of its respective owner.    
HRA-DL has no partnership, sponsorship or endorsement with HIGHRESAUDIO.    
