# Mundus News Digest Generator - Web Application

A platform-agnostic browser-based version of the Mundus News Digest Generator that runs on both Windows and Mac systems.

## 🌟 Features

- **Cross-Platform**: Runs in any modern web browser (Chrome, Firefox, Safari, Edge)
- **Real-time Progress Tracking**: Live updates with WebSocket communication
- **Drag & Drop Interface**: Easy file upload with drag-and-drop support
- **Multi-Country Support**: Sweden, Finland, and Poland processing variants
- **Professional Output**: Generates the same high-quality reports as the desktop version
- **Mobile Responsive**: Works on tablets and mobile devices
- **Background Processing**: Non-blocking file processing with live terminal output

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8 or higher**
2. **OpenAI API Key** (for AI summarization)

### Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Launch the Application**:
   ```bash
   python run_web_app.py
   ```

4. **Access the Application**:
   - The application will automatically open in your default browser
   - Or manually navigate to: `http://localhost:5000`

## 🖥️ Platform Compatibility

### Windows
- **Tested on**: Windows 10, Windows 11
- **Browsers**: Chrome, Edge, Firefox
- **Launch**: Double-click `run_web_app.py` or run from command prompt

### macOS
- **Tested on**: macOS 10.15+
- **Browsers**: Safari, Chrome, Firefox
- **Launch**: Run `python3 run_web_app.py` from Terminal

### Linux
- **Compatible**: Ubuntu, Debian, CentOS, etc.
- **Browsers**: Any modern browser
- **Launch**: Run `python3 run_web_app.py` from terminal

## 📱 Usage Instructions

### 1. Select Country
Choose your target country (Sweden, Finland, or Poland) from the dropdown menu.

### 2. Upload Files
- **Drag & Drop**: Drag markdown (.md) files directly onto the upload area
- **Browse**: Click "Browse Files" to select files using the file dialog
- **Multiple Files**: Upload multiple files at once

### 3. Process Files
Click "Generate Monthly Digest" to start the processing pipeline:

1. **News Extraction**: Parse markdown files and extract news articles
2. **Story Chaining**: Use AI to identify related stories
3. **Story Merging**: Combine related articles into coherent narratives
4. **AI Summarization**: Generate concise summaries using GPT-4
5. **Content Categorization**: Classify stories into relevant categories
6. **Document Generation**: Create professional Word documents

### 4. Download Results
Once processing completes, download the generated ZIP file containing:
- CSV/Excel files with processed data
- Markdown digest file
- Professional Word document with your organization's branding

## 🔧 Technical Architecture

### Backend (Flask + SocketIO)
- **Flask**: Web framework for HTTP requests and file handling
- **Flask-SocketIO**: Real-time communication for progress updates
- **Background Processing**: Threaded processing to prevent UI blocking
- **Session Management**: Unique sessions for concurrent users

### Frontend (Bootstrap + Vanilla JS)
- **Responsive Design**: Bootstrap 5 for mobile-first responsive layout
- **Real-time Updates**: WebSocket connection for live progress tracking
- **Modern UI**: Professional interface matching desktop application
- **File Management**: Drag-and-drop with visual feedback

### Processing Pipeline
- **Identical Logic**: Same processing algorithms as desktop version
- **Country Variants**: Dynamic module loading for country-specific processing
- **Error Handling**: Comprehensive error handling with user feedback
- **Output Management**: Organized file structure with downloadable results

## 🌐 Network Access

### Local Access
- Default: `http://localhost:5000`
- Local network: `http://[your-ip]:5000`

### Multi-Device Access
The application runs on `0.0.0.0:5000`, making it accessible from:
- Other computers on your network
- Tablets and mobile devices
- Virtual machines

Find your IP address:
- **Windows**: `ipconfig`
- **Mac/Linux**: `ifconfig` or `ip addr`

## 🔒 Security Considerations

### Local Network Only
- The application is designed for local/internal network use
- No authentication system (suitable for trusted environments)
- File uploads are stored temporarily and cleaned up automatically

### API Key Protection
- Store OpenAI API key in `.env` file (never commit to version control)
- Consider using environment variables in production environments

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'flask'"**
   ```bash
   pip install -r requirements.txt
   ```

2. **"OpenAI API key is missing"**
   - Create `.env` file with `OPENAI_API_KEY=your_key`

3. **Port 5000 already in use**
   - Change port in `run_web_app.py`: `port=5001`

4. **Browser doesn't open automatically**
   - Manually navigate to `http://localhost:5000`

5. **Files not uploading**
   - Ensure files have `.md` extension
   - Check file permissions

### Performance Tips

- **Large Files**: Processing 30+ days of news can take 15-30 minutes
- **Memory Usage**: Close other applications if processing large datasets
- **Network**: Stable internet connection required for OpenAI API calls

## 📊 Comparison with Desktop Version

| Feature | Desktop (Tkinter) | Web Application |
|---------|-------------------|-----------------|
| **Platform** | Windows/Mac/Linux | Any Browser |
| **Installation** | Python + Dependencies | Python + Dependencies |
| **Interface** | Native GUI | Modern Web UI |
| **File Selection** | File Dialog | Drag & Drop + Browse |
| **Progress Tracking** | Progress Bar | Real-time WebSocket |
| **Terminal Output** | Text Widget | Live Terminal Display |
| **Multi-User** | Single User | Multiple Sessions |
| **Mobile Support** | No | Yes (Responsive) |
| **Processing Logic** | Identical | Identical |
| **Output Quality** | Same | Same |

## 🔄 Migration from Desktop Version

The web application provides identical functionality to the desktop version:

- **Same Processing Pipeline**: All 6 steps work identically
- **Same AI Models**: Uses GPT-4.1 for summarization
- **Same Training Data**: Uses existing Excel training files
- **Same Output Format**: Generates identical Word documents
- **Same Country Support**: Sweden, Finland, Poland variants

Simply use the web version instead of running `NewsProcessorGUI.py`.

## 🆘 Support

For technical support or feature requests:
1. Check this README for common solutions
2. Verify all dependencies are installed correctly
3. Ensure `.env` file contains valid OpenAI API key
4. Test with a small number of files first

## 🎯 Future Enhancements

Potential improvements for future versions:
- User authentication system
- Cloud deployment options
- Batch processing queue
- Email notifications when processing completes
- Integration with cloud storage services
- Advanced customization options
