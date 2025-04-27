#!/bin/bash
# Startup Surface Validation System Boot Integration
# This script integrates the Startup Surface Validation system into the system boot process.

# Set the base path to the Promethios installation directory
PROMETHIOS_BASE_PATH="/home/ubuntu/personal-ai-agent"

# Create the systemd service file
cat > /tmp/promethios-startup-validation.service << 'EOF'
[Unit]
Description=Promethios Startup Surface Validation
After=network.target
Before=promethios.service

[Service]
Type=oneshot
User=ubuntu
Environment="PROMETHIOS_BASE_PATH=/home/ubuntu/personal-ai-agent"
WorkingDirectory=/home/ubuntu/personal-ai-agent
ExecStart=/usr/bin/python3 -m app.startup_validation.validate
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create the boot script that will be called during system startup
cat > ${PROMETHIOS_BASE_PATH}/scripts/startup_validation.sh << 'EOF'
#!/bin/bash
# Promethios Startup Surface Validation Boot Script

# Set the base path to the Promethios installation directory
PROMETHIOS_BASE_PATH="/home/ubuntu/personal-ai-agent"

# Log file for boot validation
LOG_FILE="${PROMETHIOS_BASE_PATH}/logs/startup_validation_boot.log"

# Ensure log directory exists
mkdir -p "${PROMETHIOS_BASE_PATH}/logs"

# Run the validation script
echo "$(date): Starting Promethios Startup Surface Validation" >> "${LOG_FILE}"
python3 -m app.startup_validation.validate --base-path="${PROMETHIOS_BASE_PATH}" >> "${LOG_FILE}" 2>&1
EXIT_CODE=$?

# Check the exit code
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "$(date): Startup validation completed successfully" >> "${LOG_FILE}"
    exit 0
elif [ ${EXIT_CODE} -eq 1 ]; then
    echo "$(date): Startup validation detected drift - system will continue with warnings" >> "${LOG_FILE}"
    exit 0
else
    echo "$(date): Startup validation failed with error code ${EXIT_CODE}" >> "${LOG_FILE}"
    exit 1
fi
EOF

# Make the boot script executable
mkdir -p ${PROMETHIOS_BASE_PATH}/scripts
chmod +x ${PROMETHIOS_BASE_PATH}/scripts/startup_validation.sh

# Create a README file explaining the boot integration
cat > ${PROMETHIOS_BASE_PATH}/app/startup_validation/README.md << 'EOF'
# Startup Surface Validation System

## Overview
The Startup Surface Validation system verifies the integrity of Promethios cognitive surfaces at system boot. It validates the Agent Cognition Index (ACI) and System Consciousness Index (PICE), generates health scores, creates drift reports, and adds memory tags without performing any automatic repairs.

## Components
- **Surface Loader**: Loads and parses the ACI and PICE JSON files
- **Validators**: Verify agents, modules, schemas, endpoints, and components
- **Health Scorer**: Calculates health scores with specified weights
- **Drift Reporter**: Generates and saves validation reports
- **Memory Tagger**: Updates system status with memory tags

## Boot Integration
The system is integrated into the boot process using one of the following methods:

### Method 1: Systemd Service (Recommended for Production)
A systemd service is provided that runs the validation script during system boot:

```bash
sudo cp /tmp/promethios-startup-validation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable promethios-startup-validation.service
sudo systemctl start promethios-startup-validation.service
```

### Method 2: Boot Script (Alternative)
A boot script is provided that can be called from other startup mechanisms:

```bash
/home/ubuntu/personal-ai-agent/scripts/startup_validation.sh
```

## Usage
The validation script can also be run manually:

```bash
python -m app.startup_validation.validate [--verbose] [--base-path=PATH]
```

Options:
- `--verbose`, `-v`: Enable verbose logging
- `--base-path`: Base path to prepend to file paths

## Exit Codes
- `0`: All surfaces validated successfully
- `1`: Surface drift detected (system will continue with warnings)
- `2`: Validation failed due to error

## Health Scoring
Surface health is calculated with the following weights:
- Agents Health: 30%
- Modules Health: 30%
- Schemas Health: 20%
- Endpoints Health: 10%
- Components Health: 10%

## Memory Tags
The system creates memory tags in the format:
- `startup_surface_validated_YYYYMMDD`: When all surfaces are valid
- `startup_surface_drift_detected_YYYYMMDD`: When drift is detected
EOF

# Create an installation script for the systemd service
cat > ${PROMETHIOS_BASE_PATH}/app/startup_validation/install_service.sh << 'EOF'
#!/bin/bash
# Install the Promethios Startup Surface Validation systemd service

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Copy the service file to systemd directory
cp /tmp/promethios-startup-validation.service /etc/systemd/system/

# Reload systemd
systemctl daemon-reload

# Enable the service
systemctl enable promethios-startup-validation.service

echo "Promethios Startup Surface Validation service installed and enabled"
echo "To start the service now, run: sudo systemctl start promethios-startup-validation.service"
EOF

# Make the installation script executable
chmod +x ${PROMETHIOS_BASE_PATH}/app/startup_validation/install_service.sh

echo "Boot integration files created successfully"
echo "To install the systemd service, run: sudo ${PROMETHIOS_BASE_PATH}/app/startup_validation/install_service.sh"
