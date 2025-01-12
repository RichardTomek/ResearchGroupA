# Research Group A
Welcome to the git repository of our Research Lab Course Experiment Pre-Testing

# Data Analysis

Data analysis files for the resulting data from the experiment can be found in the **data_analysis** directory.

# Experiment setup

## Initial Setup

### 1. Open Terminal

**Windows:**
1. Press `Win + R`
2. Type `cmd` and press Enter
3. Navigate to your project directory:
```bash
cd path\to\ResearchGroupA
```

**Mac:**
1. Press `Cmd + Space`
2. Type `terminal` and press Enter
3. Navigate to your project directory:
```bash
cd path/to/ResearchGroupA
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

With your virtual environment activated, install the required packages:

**Windows & Mac:**
```bash
# Install oTree
pip install otree

# Install the Frisbee package by 
# Wüst, Fabian A. (2024). frisbee-otree-extension [Private repository]. GitHub.
# As the repository is private we cannot provide it here on our own.
cd frisbee-otree-extension-dev/
pip install .
cd ../
```

## Running the Server

### Start the oTree Development Server

**Windows:**
```bash
cd experiment
otree devserver
```

**Mac:**
```bash
cd experiment
otree devserver
```

The server will start and be accessible at `http://localhost:8000`

### Start the Frisbee server

To run Frisbee server that deals with the connection of OTree and clients connected to Polar H10 sensors please follow the
instructions provided in the README.md file of Wüst, Fabian A. (2024). frisbee-otree-extension [Private repository]. GitHub.

### Troubleshooting

If the there is an error with ip 127.0.0.1 and port 8001 already being in use, forcefully kill the frisbee websocket server using
```bash
kill -9 $(lsof -ti :8001)
```

## Running Clients

Open a new terminal window/tab for each client you want to run. Make sure to activate the virtual environment in each new terminal.

### Activate Virtual Environment in New Terminal

**Windows:**
```bash
cd path\to\ResearchGroupA
venv\Scripts\activate
```

**Mac:**
```bash
cd path/to/ResearchGroupA
source venv/bin/activate
```

### Running Frisbee clients

To run Frisbee clients connected to Polar H10 sensors that send the data to the Frisbee server please follow the
instructions provided in the README.md file of Wüst, Fabian A. (2024). frisbee-otree-extension [Private repository]. GitHub.


