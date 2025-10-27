# DCM GUI Documentation

## Overview

This is the Device Controller-Monitor (DCM) graphical interface for the pacemaker system. It provides a complete frontend for doctors and technicians to configure pacemaker parameters and manage the device.

## Running the Application

From the DCM directory:
```bash
python3 run_dcm.py
```

Or directly:
```bash
python3 -m gui.dcm_gui
```

## Features

### User Authentication
- Login system with secure password storage 
- User registration (maximum 10 users)
- Session management

### Pacing Modes
The interface supports four pacing modes:
- **AOO**: Atrium paced, none sensed, none response
- **VOO**: Ventricle paced, none sensed, none response
- **AAI**: Atrium paced, atrium sensed, inhibit response
- **VVI**: Ventricle paced, ventricle sensed, inhibit response

### Parameter Management
The GUI displays different parameters depending on the selected mode:

**AOO Mode:**
- Lower Rate Limit (LRL)
- Atrial Amplitude
- Atrial Pulse Width

**VOO Mode:**
- Lower Rate Limit (LRL)
- Ventricular Amplitude
- Ventricular Pulse Width

**AAI Mode:**
- Lower Rate Limit (LRL)
- Upper Rate Limit (URL)
- Atrial Amplitude
- Atrial Pulse Width
- Atrial Refractory Period (ARP)

**VVI Mode:**
- Lower Rate Limit (LRL)
- Upper Rate Limit (URL)
- Ventricular Amplitude
- Ventricular Pulse Width
- Ventricular Refractory Period (VRP)

### Parameter Validation
All parameters are validated according to the pacemaker specification:
- LRL: 30-175 ppm
- URL: 50-175 ppm (must be greater than LRL)
- Amplitudes: 0.1-5.0 V
- Pulse Widths: 0.1-1.9 ms
- Refractory Periods: 150-500 ms

### Save and Load
- Save current parameters to file (JSON format)
- Load previously saved parameters

### Status Monitoring
The interface includes a status bar showing:
- Telemetry status (currently shows "Disconnected" as hardware is not implemented yet)
- Device connection status
- Visual LED indicator

## User Workflow

### First Time Setup
1. Launch the application
2. Click "Register New User"
3. Enter username (minimum 3 characters) and password (minimum 4 characters)
4. Confirm password and register
5. Login with your credentials

### Using the Interface
1. Select a pacing mode by clicking one of the four mode buttons
2. The parameter form will update to show only relevant parameters
3. Edit parameter values as needed
4. Click "Save Parameters" to validate and save
5. Click "Load Parameters" to restore saved values
6. Click "Logout" when finished

## Technical Details

### File Structure
```
DCM/
├── gui/
│   ├── dcm_gui.py          # Main application
│   └── __init__.py
├── core/
│   ├── user_management.py  # Authentication
│   ├── params.py           # Parameter handling
│   └── modes.py            # Mode definitions
├── storage/
│   ├── users.json          # User credentials
│   └── params.json         # Saved parameters
└── run_dcm.py              # Launch script
```

### Backend Integration
The GUI integrates with the backend modules:
- `user_management`: Handles authentication and user database
- `params`: Manages parameter validation and persistence
- `modes`: Defines pacing mode information

### Data Storage
- User credentials are stored in `storage/users.json` with hashed passwords
- Parameter configurations are stored in `storage/params.json`
- Both files use JSON format for easy inspection and debugging

## Requirements

This implementation satisfies the Deliverable 1 requirements:
- User login and registration system
- Mode selection interface
- Parameter input with mode-specific display
- Parameter validation per specification
- Communication status indicators (placeholder for hardware)
- Parameter save/load functionality

## Notes

- This is Deliverable 1 which focuses on the GUI frontend only
- Hardware communication features show placeholders and will be implemented in future deliverables
- The "Disconnected (No Hardware)" status is expected for this deliverable
