# Core

This directory contains the backend libraries for the DCM. Here is a description of all of them. 

# egram Module

This module provides classes for buffering and managing Egram (electrogram) signal data. It supports multiple channels and keeps only the most recent N samples per channel.

## Classes

### EgramSample

A data structure representing a single Egram sample.

Attributes:
- timestamp (float): The time at which the sample was recorded.
- channel (str): The channel name (e.g., "atrial", "ventricular", "surface").
- value (float): The recorded signal value.

### EgramBuffer

Buffers Egram data by channel and keeps only the N most recent values per channel.

#### Constructor

- __init__(maxlen: int = 1000)
  - Initializes the buffer with a maximum length per channel.
  - Arguments:
    - maxlen (int): Maximum number of samples to store per channel.

#### Methods

- add_sample(channel: str, value: float, timestamp: float = None) -> None  
  Adds a new Egram sample to the specified channel.  
  Arguments:
    - channel (str): The name of the channel to add the sample to.
    - value (float): The sample value.
    - timestamp (float, optional): The timestamp of the sample. If not provided, the current time is used.

- get_recent(channel: str, n: int) -> List[EgramSample]  
  Returns the n most recent samples for a given channel.  
  Arguments:
    - channel (str): The channel name.
    - n (int): The number of recent samples to retrieve.

- get_all(channel: str) -> List[EgramSample]  
  Returns all samples currently stored for the specified channel.  
  Arguments:
    - channel (str): The channel name.

- clear() -> None  
  Clears all stored samples from all channels.

# mode Module

This module defines pacemaker operation modes and provides utilities to parse and describe them in human-readable form.

## Classes

### ModeInfo
A data structure representing the parsed details of a pacemaker mode.

Attributes:
- paced (str): The chamber being paced.
- sensed (str): The chamber being sensed.
- response (str): The response type to a sensed event.
- descrpt (str): A textual description of the mode.

### PaceMakerMode
An enumeration of supported pacemaker modes.

Members:
- AOO: Atrium paced, Atrium sensed, no response.
- VOO: Ventricle paced, Ventricle sensed, no response.
- AAI: Atrium paced, Atrium sensed, Inhibited response.
- VVI: Ventricle paced, Ventricle sensed, Inhibited response.

## Functions

- parse_mode(mode: PaceMakerMode | str) -> ModeInfo  
  Parses a pacemaker mode into its components (paced, sensed, response) and returns a `ModeInfo` object.  
  Arguments:
    - mode (PaceMakerMode or str): The mode to parse, either as an enum member or 3-letter string.

- list_modes() -> Dict[str, str]  
  Returns a dictionary of available pacemaker modes and their corresponding textual descriptions.


# parameters Module

This module defines the pacemaker programmable parameters and provides utilities for validation, serialization, and persistence to JSON storage.

## Classes

### Parameters
A data class representing the programmable parameters of the pacemaker.

Attributes:
- LRL (int): Lower Rate Limit (ppm).
- URL (int): Upper Rate Limit (ppm).
- atrial_amp (float): Atrial pulse amplitude (V).
- atrial_width (float): Atrial pulse width (ms).
- ventricular_amp (float): Ventricular pulse amplitude (V).
- ventricular_width (float): Ventricular pulse width (ms).
- VRP (int): Ventricular Refractory Period (ms).
- ARP (int): Atrial Refractory Period (ms).

#### Methods
- validate() -> bool  
  Ensures all parameters fall within the valid ranges defined in Appendix A.  
  Raises a ValueError if any parameter is out of range.

- to_dict() -> Dict[str, Any]  
  Converts the Parameters object into a dictionary for serialization.

## Functions

- save_parameters(params: Parameters) -> None  
  Saves a validated Parameters object to a JSON file defined by `PARAMS_FILE`.  
  Arguments:
    - params (Parameters): The Parameters instance to save.

- load_parameters() -> Parameters  
  Loads parameters from the JSON file and returns a Parameters object.  
  Raises FileNotFoundError if the file does not exist.

- reset_parameters_file() -> None  
  Resets the parameters JSON file by overwriting it with an empty dictionary.

  # user_manager Module

This module provides a simple local user management system with support for registration, authentication, listing, and deletion.  
User credentials are securely stored in a JSON file with SHA256 password hashing.

## Constants
- USER_FILE: Path to the JSON file storing user credentials.
- MAX_USERS (int): Maximum number of users allowed in the system (default: 10).

## Internal Functions
(Used internally; not part of the public API)

- _loadUsers() -> Dict[str, str]  
  Loads user data from the JSON file. Returns a dictionary mapping usernames to hashed passwords.

- _saveUsers(users: Dict[str, str]) -> None  
  Saves user data to the JSON file.

- _hashPassword(password: str) -> str  
  Hashes a plaintext password using SHA256 and returns the resulting hash.

## Public Functions

- register_user(username: str, password: str) -> bool  
  Registers a new user with a hashed password.  
  Returns True if registration succeeds, or False if the username is taken or the maximum user limit is reached.  
  Arguments:
    - username (str): The desired username.
    - password (str): The plaintext password.

- authenticate_user(username: str, password: str) -> bool  
  Authenticates a user by verifying the password.  
  Returns True if credentials are valid, otherwise False.  
  Arguments:
    - username (str): The username to authenticate.
    - password (str): The plaintext password.

- list_users() -> List[str]  
  Returns a list of all registered usernames.

- remove_user(username: str) -> bool  
  Removes a user from the system.  
  Returns True if the user existed and was removed, False otherwise.  
  Arguments:
    - username (str): The username to remove.

- reset_users() -> None  
  Clears all users from the system by overwriting the JSON file with an empty dictionary.