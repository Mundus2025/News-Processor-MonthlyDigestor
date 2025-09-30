# 🌟 Mundus News Digest Generator 2.0

**Transform daily news markdown files into professional monthly reports with AI-powered summaries and categorization.**

[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-brightgreen)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/License-Proprietary-red)]()
[![Version](https://img.shields.io/badge/Version-2.0-orange)]()

## 🚀 What's New in Version 2.0

### 🌐 **Web-Based Interface**
- **Browser-based application** - No more desktop GUI limitations
- **Cross-platform compatibility** - Works on Windows, Mac, and Linux
- **Mobile responsive** - Use on tablets and phones
- **Real-time progress tracking** - WebSocket-powered live updates
- **Multi-user support** - Multiple people can process files simultaneously

### 🎯 **User-Friendly Launch**
- **Double-click to start** - No command line knowledge required
- **Automatic setup** - Handles Python dependencies automatically  
- **Interactive API key setup** - Guided OpenAI configuration
- **Professional interface** - Modern Bootstrap-based design

### ⚡ **Enhanced Performance**
- **Smart dependency checking** - Only installs what's needed
- **Background processing** - Non-blocking UI operations
- **Optimized downloads** - ZIP files with only final outputs
- **GPT-4.1 integration** - Latest OpenAI model for better results

---

## 📋 Quick Start

### 🌐 **Cloud Hosted Version** ⭐ (Recommended)
```
🔗 Visit: https://mundus-news-digest.onrender.com
✅ No installation required
✅ Works on any device with internet
✅ No Mac security issues
```

### 💻 **Local Installation** (Alternative)

#### 🍎 **Mac Users**
```bash
# First time: Right-click → Open (to bypass security)
# Then simply double-click:
Mundus News Digest.command
```

#### 🪟 **Windows Users**  
```bash
# Simply double-click:
Mundus News Digest.bat
```

#### 🌐 **All Platforms**
```bash
python run_web_app.py
# Then visit: http://localhost:5000
```

**🌟 For the easiest experience, use the cloud-hosted version above!**

---

## 🔧 Installation & Setup

### Prerequisites
- **Python 3.8+** (will be checked automatically)
- **Internet connection** (for AI processing)
- **OpenAI API key** (guided setup included)

### First-Time Setup
1. **Get an OpenAI API key**:
   - Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Create account and generate a key starting with `sk-`

2. **Launch the application**:
   - **Mac**: Double-click `Mundus News Digest.command`
   - **Windows**: Double-click `Mundus News Digest.bat`

3. **Follow the prompts**:
   - Enter your API key when prompted
   - Wait for automatic dependency installation
   - Browser opens automatically

### Manual Setup (Optional)
```bash
# Install dependencies manually
pip install -r requirements.txt

# Create environment file
echo "OPENAI_API_KEY=your_key_here" > .env

# Start application
python run_web_app.py
```

---

## 📖 How to Use

### 1. **Select Country**
Choose your target country for specialized processing:
- 🇸🇪 **Sweden** (default)
- 🇫🇮 **Finland** 
- 🇵🇱 **Poland**

### 2. **Upload Files**
- **Drag & Drop**: Drag `.md` files onto the upload area
- **Browse**: Click "Browse Files" to select manually
- **Multiple Files**: Upload many files at once

### 3. **Process Files**
Click **"Generate Monthly Digest"** and watch real-time progress:
1. 📄 **News Extraction** - Parse markdown files
2. 🔗 **Story Chaining** - Link related articles using AI
3. 🔄 **Story Merging** - Combine related stories
4. 🧠 **AI Summarization** - Generate summaries with GPT-4.1
5. 📊 **Categorization** - Classify stories by topic
6. 📄 **Document Generation** - Create professional Word documents

### 4. **Download Results**
Get a ZIP file containing:
- **Monthly_News_Digest_[Country].md** - Markdown format
- **Monthly_News_Digest_[Country].docx** - Professional Word document

---

## 🏗️ Architecture

### Processing Pipeline
```mermaid
graph LR
    A[Markdown Files] --> B[News Extraction]
    B --> C[Story Chaining]
    C --> D[Story Merging]
    D --> E[AI Summarization]
    E --> F[Categorization]
    F --> G[Document Generation]
    G --> H[Professional Output]
```

### Technology Stack
- **Backend**: Flask + SocketIO for real-time communication
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **AI Processing**: OpenAI GPT-4.1
- **Data Processing**: Pandas, scikit-learn
- **Document Generation**: python-docx
- **File Formats**: Markdown, CSV, Excel, Word

### Country-Specific Processing
Each country has specialized:
- **Government institutions** (Riksdag, Eduskunta, Sejm)
- **Central banks** (Riksbank, Bank of Finland, NBP)
- **Category definitions** tailored to national context
- **Language conventions** (British English maintained)

---

## 📁 Project Structure

```
Mundus-News-Processor/
├── 🌐 Web Application
│   ├── app.py                          # Flask web server
│   ├── run_web_app.py                  # Cross-platform launcher
│   ├── templates/index.html            # Web interface
│   ├── static/css/style.css            # Modern styling
│   └── static/js/app.js                # Frontend logic
│
├── 🖥️ Desktop Version (Legacy)
│   └── NewsProcessorGUI.py             # Original Tkinter GUI
│
├── 🔧 Processing Scripts
│   ├── NewsToCsv.py                    # News extraction
│   ├── NewsChainer.py                  # Story linking
│   ├── NewsMerger.py                   # Story combination
│   ├── NewsSummariser.py               # AI summarization
│   ├── NewsDigestor.py                 # Content categorization
│   └── NewsToDocx.py                   # Document generation
│
├── 🌍 Country Variants
│   ├── Finland*.py                     # Finnish processing
│   └── Poland*.py                      # Polish processing
│
├── 🚀 User-Friendly Launchers
│   ├── Mundus News Digest.command     # Mac double-click
│   ├── Mundus News Digest.bat         # Windows double-click
│   ├── Mundus News Digest.app/        # Mac app bundle
│   ├── start_web_app.sh               # Linux/Mac script
│   └── start_web_app.bat              # Windows script
│
├── 📚 Documentation
│   ├── README.md                       # This file
│   ├── USER_GUIDE_Non_Technical.md     # Beginner guide
│   ├── README_Web_Application.md       # Technical details
│   └── WEB_APPLICATION_SUMMARY.md      # Conversion summary
│
├── 📊 Training Data
│   └── TrainingData/                   # ML training datasets
│
└── 🔧 Configuration
    ├── requirements.txt                # Python dependencies
    ├── .env                           # API keys (create this)
    └── Mundus_Icon.png               # Application logo
```

---

## 🎯 Features

### 🌟 **Core Capabilities**
- ✅ **AI-Powered Summarization** - GPT-4.1 generates concise, professional summaries
- ✅ **Smart Story Chaining** - Links related articles across multiple days
- ✅ **Automatic Categorization** - ML + AI hybrid classification system
- ✅ **Multi-Country Support** - Specialized processing for Sweden, Finland, Poland
- ✅ **Professional Output** - Branded Word documents with table of contents

### 🚀 **Version 2.0 Enhancements**
- ✅ **Web Interface** - Modern, responsive browser-based UI
- ✅ **Real-Time Progress** - Live updates with WebSocket communication
- ✅ **Cross-Platform** - Works on any device with a browser
- ✅ **Multi-User** - Concurrent processing sessions
- ✅ **Mobile Support** - Responsive design for tablets/phones
- ✅ **Smart Setup** - Automatic dependency management
- ✅ **User-Friendly** - No technical knowledge required

### 🔧 **Technical Features**
- ✅ **Background Processing** - Non-blocking server operations
- ✅ **Session Management** - Isolated workspaces per user
- ✅ **Error Recovery** - Comprehensive error handling
- ✅ **File Management** - Automatic cleanup and organization
- ✅ **Network Access** - Accessible from any device on network

---

## 📊 Performance

### Processing Speed
- **30 days of news**: ~15-30 minutes (depending on content volume)
- **Real-time updates**: Live progress tracking via WebSocket
- **Concurrent users**: Multiple sessions supported simultaneously

### System Requirements
- **CPU**: Modern multi-core processor recommended
- **RAM**: 4GB minimum, 8GB recommended for large datasets
- **Storage**: 500MB free space for processing
- **Network**: Stable internet connection for AI processing

### Supported File Formats
- **Input**: Markdown (.md) files with structured news content
- **Output**: Markdown (.md) and Word (.docx) documents
- **Intermediate**: CSV and Excel files for data analysis

---

## 🔒 Security & Privacy

### Data Handling
- ✅ **Local Processing** - Files processed on your computer
- ✅ **Temporary Storage** - Automatic cleanup after processing
- ✅ **Session Isolation** - Each user gets separate workspace
- ✅ **API Key Security** - Stored in local .env file only

### OpenAI Integration
- ✅ **Text-Only** - Only article text sent for summarization
- ✅ **No File Upload** - Original files never leave your system
- ✅ **Secure API** - Industry-standard OpenAI API usage
- ✅ **Rate Limiting** - Automatic handling of API limits

---

## 🆘 Troubleshooting

### Common Issues

#### **"Python not found"**
- **Mac**: Install from [python.org](https://python.org/downloads/)
- **Windows**: Install Python and check "Add Python to PATH"

#### **"Dependencies failed to install"**
- Check internet connection
- Try running setup scripts as administrator
- Use `pip install -r requirements.txt` manually

#### **"OpenAI API key missing"**
- Get key from [OpenAI API Keys](https://platform.openai.com/api-keys)
- Create `.env` file with `OPENAI_API_KEY=your_key_here`

#### **"Browser doesn't open"**
- Manually visit `http://localhost:5000`
- Try different browser (Chrome, Firefox, Safari)
- Check if port 5000 is available

#### **Processing takes too long**
- Normal for large datasets (30+ days of news)
- Keep terminal window open during processing
- Ensure stable internet connection for AI calls

#### **Mac: "Permission denied" or "Access privileges" error**
- **Right-click** the `.command` file → Select **"Open"** → Click **"Open"** in dialog
- Or run in Terminal: `chmod +x "Mundus News Digest.command"`
- Or check **System Preferences** → **Security & Privacy** → Click **"Open Anyway"**

### Performance Tips
- Process files in batches of 30 days or less
- Close other applications during heavy processing
- Use wired internet connection for stability
- Keep system updated for optimal performance

---

## 📈 Version History

### Version 2.0 (Current)
- 🌐 **Web-based interface** replacing desktop GUI
- 🚀 **Cross-platform compatibility** (Windows, Mac, Linux)
- 📱 **Mobile responsive** design
- ⚡ **Real-time progress** tracking with WebSocket
- 🎯 **User-friendly launchers** for non-technical users
- 🧠 **GPT-4.1 integration** for improved AI processing
- 🔧 **Smart dependency management**
- 👥 **Multi-user support** with session isolation

### Version 1.x (Legacy)
- 🖥️ **Desktop GUI** with Tkinter
- 🔧 **Single-user** processing
- 📊 **Platform-specific** installation
- 🧠 **GPT-4-turbo** AI processing
- 📁 **Local file** processing only

---

## 🤝 Contributing

This is a proprietary project. For feature requests or bug reports, please contact the development team.

### Development Setup
```bash
# Clone repository
git clone [repository-url]
cd News-Processor

# Install development dependencies
pip install -r requirements.txt

# Set up environment
cp env_template.txt .env
# Edit .env with your OpenAI API key

# Run in development mode
python run_web_app.py
```

---

## 📄 License

© 2025 Mundus. All rights reserved. Proprietary software.

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4.1 language model
- **Flask & SocketIO** - Web framework and real-time communication
- **Bootstrap** - Frontend UI framework
- **scikit-learn** - Machine learning capabilities
- **python-docx** - Document generation

---

## 📞 Support

For technical support or questions:
1. Check the **troubleshooting section** above
2. Review the **USER_GUIDE_Non_Technical.md** for detailed instructions
3. Ensure all prerequisites are properly installed
4. Contact the development team for additional assistance

---

**🎉 Ready to transform your news processing workflow? Get started with Mundus News Digest Generator 2.0!**
