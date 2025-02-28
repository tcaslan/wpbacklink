# WPBacklink - WordPress Backlink Bot with Modern GUI

WPBacklink is a powerful and user-friendly application designed to automate comment submissions on WordPress sites. It features a modern, customizable interface with both light and dark themes, comprehensive logging, and robust configuration options.

![WPBacklink](https://i.imgur.com/TqHW33Q.png)

## 🌟 Features

### Modern User Interface
- **Sleek Design**: Clean, modern interface built with CustomTkinter
- **Theme Support**: Toggle between light and dark modes
- **Multi-language Support**: Available in English and Turkish
- **Responsive Layout**: Adapts to different window sizes

### Core Functionality
- **Automated Comments**: Submit comments to WordPress sites automatically
- **Link Management**: Load and manage target WordPress site links
- **Comment Configuration**: Customize author name, email, URL, and comment text
- **Success Tracking**: Keep track of successfully processed links

### Advanced Features
- **Real-time Logging**: Comprehensive activity log with color-coded message types
- **Progress Tracking**: Monitor progress with percentage and visual indicators
- **Process Control**: Start, pause, and stop the process at any time
- **Statistics**: Track performance metrics and success rates
- **Configuration Management**: Save and load your settings

## 📋 Requirements

- Python 3.6 or higher
- Internet connection
- Dependencies listed in `requirements.txt`

## 🚀 Installation

1. Clone this repository or download the source code:
   ```
   git clone https://github.com/yourusername/wpbacklink.git
   cd wpbacklink
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## 🔧 Usage

### Starting the Application

Run the application using:
```
python gui.py
```

### Main Tab

The main tab provides controls for the backlink process:

1. **Link File Selection**:
   - Enter the path to your links file or use the "Browse" button
   - Click "Load" to load the links

2. **Process Controls**:
   - **Start**: Begin the backlink process
   - **Pause**: Temporarily pause the process
   - **Stop**: Stop the process completely

3. **Progress Monitoring**:
   - Current link being processed
   - Progress bar showing completion percentage
   - Activity log showing real-time updates

### Settings Tab

Configure your comment settings:

1. **Comment Information**:
   - Author Name: The name that will appear on comments
   - Email: Email address for the comment author
   - Website URL: Your website that will be linked
   - Comment Text: The content of your comments (supports HTML)

2. **Process Settings**:
   - Success File: Where successfully processed links are saved
   - Delay: Time to wait between requests (in seconds)
   - Language: Select interface language

3. **Configuration Management**:
   - Save: Save current settings
   - Reset: Reset to default settings

### Statistics Tab

Monitor your backlink campaign performance:

- Total links processed
- Successful submissions
- Failed submissions
- Success rate
- Average processing time
- Export statistics to CSV

## 📁 File Formats

### Links File
A text file with one URL per line, pointing to WordPress posts where you want to leave comments.

Example:
```
https://example.com/blog-post-1
https://example.com/blog-post-2
https://anothersite.com/article
```

### Configuration File
The application saves and loads settings from a `bot_config.json` file in the same directory.

Example:
```json
{
    "author": "John Doe",
    "email": "john@example.com",
    "url": "https://example.com",
    "comment": "Great article! Check out my site at <a href='https://example.com'>example.com</a>",
    "success_file": "success.txt",
    "delay": "3",
    "language": "en"
}
```

## 🛠️ Advanced Configuration

### Custom Post Data

You can modify the `postData.json` file to customize the data structure used for comment submissions:

```json
{
    "author": "Your Name",
    "email": "your@email.com",
    "url": "https://yoursite.com/",
    "comment": "Your comment with <a href='https://yoursite.com/'>HTML link</a>",
    "comment_post_ID":"",
    "comment_parent":"",
    "submit": "Post Comment",
    "ak_js":""
}
```

### Customizing the User Interface

The application uses the `ThemeAndIcons` class to manage the visual appearance. You can modify the color scheme by editing the `THEME` dictionary in `gui.py`.

## ⚠️ Disclaimer

Using this tool to submit automated comments to websites may violate the terms of service of those websites. This tool is provided for educational purposes only. Use responsibly and at your own risk.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.

---

Made with ❤️ by [Your Name] 
