# Trace - Investigation Toolkit

![Trace Logo](icons/AppIcon.icns)

Trace is a powerful investigation toolkit designed to streamline and automate investigative workflows. Built with Python and featuring a modern UI, Trace helps investigators collect, analyze, and manage data efficiently.

## Features

- **Automated Investigation Tools**: Streamlined tools for data collection and analysis
- **Update System**: Built-in update manager for seamless version updates
- **Modern UI**: Clean, intuitive interface built with tkinter
- **Desktop Integration**: Automatic desktop shortcut creation
- **SSL Certificate Management**: Built-in certificate handling for secure connections

## Quick Start

### Installation

1. Download the latest `Trace-Installer.pkg` from the [Releases](https://github.com/phamilton09/Trace/releases) page
2. Double-click to open the installer
3. Follow the installation prompts
4. Launch Trace from your Applications folder or desktop shortcut

### System Requirements

- macOS 10.15 or later
- Internet connection (for initial setup and updates)
- Administrator privileges (for installation)

## Development

### Prerequisites

- Python 3.13 or later
- pip (Python package manager)
- Git

### Building from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/phamilton09/Trace.git
   cd Trace
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python3 Trace_v1.py
   ```

### Building the Installer

To create a new installer package:

```bash
python3 build_installer.py
```

This will create a `Trace-Installer.pkg` file in your Desktop directory.

## Project Structure

```
Trace/
├── Trace_v1.py           # Main application
├── update_manager.py     # Update system
├── install_certificates.py # SSL certificate management
├── build_installer.py    # Installer builder
├── installer.py         # Installation utilities
├── requirements.txt     # Python dependencies
├── alert_templates/     # Alert template files
└── icons/              # Application icons
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For issues, feature requests, or questions:
1. Check the [documentation](https://github.com/phamilton09/Trace/wiki)
2. Open an [issue](https://github.com/phamilton09/Trace/issues)
3. Contact the development team

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Python community for the excellent libraries
- Contributors and testers
- The investigation community for feedback and suggestions

---

*Built with ❤️ for investigators* 