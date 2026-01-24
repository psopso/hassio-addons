# X728 GPIO Button Manager

This add-on manages the logic for the Geekworm X728 UPS button on Raspberry Pi 4.

## Features

* **GPIO12**: Maintains HIGH state to enable XUPS management. (Boot OK signal).

* **GPIO5**: Monitors button press:
    - Press on-board blue button 1-2 seconds to reboot
    - Press on-board blue button 3 seconds to safe shutdown
    - Press on-board blue button 7-8 seconds to force shutdown

## Requirements

Ensure the following are set in your addon configuration:
* "privileged": ["SYS_ADMIN", "SYS_RAWIO"]
* "host_control": true