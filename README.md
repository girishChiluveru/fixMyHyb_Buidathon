# FixMyHyd - AI-Powered Civic Issue Reporting System

A modern, AI-powered platform for reporting and tracking civic issues in Hyderabad. Citizens can easily report issues through photos and voice notes, while administrators can manage and track complaint resolution.

## Features

### For Citizens
- **Easy Reporting**: Upload photos and voice notes to report civic issues
- **AI-Powered Analysis**: Automatic categorization and priority assessment
- **Multi-language Support**: Report in Telugu, Hindi, or English
- **Real-time Tracking**: Monitor complaint status and progress
- **Modern Dashboard**: Clean, intuitive interface for managing reports

### For Administrators
- **Comprehensive Dashboard**: Overview of all complaints and statistics
- **Status Management**: Update complaint status and add comments
- **Advanced Filtering**: Filter complaints by status, category, and more
- **Data Export**: Export complaint data for analysis
- **Real-time Updates**: Track resolution progress and citizen satisfaction

### AI Capabilities
- **Image Analysis**: Automatic issue detection and categorization
- **Voice Transcription**: Convert voice notes to text in multiple languages
- **Smart Categorization**: Classify issues into appropriate categories
- **Priority Assessment**: Determine urgency based on content analysis
- **Formal Report Generation**: Create structured complaints for GHMC submission

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **AI/ML**: Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript
- **Image Processing**: Pillow (PIL)
- **Authentication**: Session-based with password hashing

## Installation

### Prerequisites
- Python 3.8 or higher
- Google AI API key (from Google AI Studio)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fixmyhyd
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.template .env
   ```
   Edit `.env` file and add your Google AI API keys:
   ```
   GOOGLE_API_KEY_IMAGE=your-api-key-here
   GOOGLE_API_KEY_AUDIO=your-api-key-here
   GOOGLE_API_KEY_TEXT=your-api-key-here
   GOOGLE_API_KEY_REPORT=your-api-key-here
   SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5001`
   - Default admin credentials: `admin` / `admin123`

## Usage

### For Citizens

1. **Register/Login**: Create an account or log in with existing credentials
2. **Report Issue**: 
   - Take a photo of the civic issue
   - Add voice description or text description
   - Provide additional location details (optional)
   - Submit the report
3. **Track Progress**: Monitor your reports in the dashboard
4. **View Details**: Click on any report to see detailed information

### For Administrators

1. **Admin Login**: Use admin credentials to access the admin dashboard
2. **View Complaints**: See all submitted complaints with filtering options
3. **Update Status**: Change complaint status and add comments
4. **Monitor Statistics**: Track resolution rates and performance metrics
5. **Export Data**: Download complaint data for analysis

## API Endpoints

### User Endpoints
- `POST /api/report-issue` - Submit a new complaint
- `GET /api/user/complaints` - Get user's complaints
- `GET /api/user/complaints/<id>` - Get specific complaint details

### Admin Endpoints
- `GET /api/admin/complaints` - Get all complaints
- `GET /api/admin/complaints/<id>` - Get complaint details
- `PUT /api/admin/complaints/<id>/status` - Update complaint status

## Database Schema

### Tables
- **users**: Citizen accounts
- **admins**: Administrator accounts
- **complaints**: Issue reports
- **status_history**: Complaint status changes

## Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `GOOGLE_API_KEY_*`: Google AI API keys for different services
- `DEBUG`: Enable/disable debug mode
- `PORT`: Application port (default: 5001)

### Complaint Categories
- Open Garbage Dump
- Sewage Leak/Overflow
- Pothole/Damaged Road
- Damaged Electrical Infrastructure
- Fallen Tree
- Water Logging
- Stray Animals
- Other

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact:
- Email: support@fixmyhyd.gov.in
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)

## Acknowledgments

- Google AI for providing the Gemini API
- Flask community for the excellent framework
- All contributors and testers

---

**FixMyHyd** - Making Hyderabad a better place, one report at a time! 🏙️✨
