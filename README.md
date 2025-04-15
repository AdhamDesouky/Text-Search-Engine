# Advanced Text Search Engine

A sophisticated text search engine that combines efficient string searching algorithms with modern web development practices. This project demonstrates the implementation of various search algorithms while providing a user-friendly interface for searching through multiple file formats.

## Features

### 1. Advanced Search Algorithms
- **Boyer-Moore Algorithm**: Efficient string searching with preprocessing
- **Knuth-Morris-Pratt Algorithm**: Linear time string matching
- **Fuzzy Search**: Find similar words using Levenshtein distance
- **Wildcard Search**: Support for * and ? patterns
- **Regular Expression Search**: Powerful pattern matching

### 2. File Format Support
- **Text Files (.txt)**: Direct text search
- **PDF Documents (.pdf)**: Text extraction and search
- **Word Documents (.docx)**: Text extraction and search
- **Real-time File Preview**: View file contents before searching

### 3. User Authentication & Management
- Secure user registration and login
- Password hashing for security
- Session management
- User-specific search history
- Personalized search experience

### 4. Search Features
- Case-sensitive/insensitive search
- Multiple search algorithms
- Context-aware results
- Line number display
- Highlighted matches
- Search statistics (time, matches)
- Export results to CSV

### 5. Modern UI/UX
- Responsive Bootstrap design
- Dark/Light mode support
- Drag-and-drop file upload
- Interactive search options
- Real-time feedback
- Clean and intuitive interface

## Technical Implementation

### Backend
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Search Algorithms**:
  - Boyer-Moore: O(n/m) average case
  - KMP: O(n + m) worst case
  - Fuzzy Search: Levenshtein distance
  - Wildcard: Pattern matching
- **File Processing**:
  - PyPDF2 for PDF extraction
  - python-docx for Word documents
  - Text file handling

### Frontend
- **Bootstrap 5**: Responsive design
- **Font Awesome**: Icons
- **JavaScript**: Interactive features
- **CSS Variables**: Theme support
- **AJAX**: Asynchronous operations

### Database
- **SQLite**: Local database
- **Models**:
  - User: Authentication
  - SearchHistory: Track searches

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/text-search-engine.git
cd text-search-engine
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Starting the Application
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000`

### 2. User Registration
1. Click "Register" in the navigation bar
2. Enter username and password
3. Confirm password
4. Submit registration
5. Log in with your credentials

### 3. Searching Files
1. Upload a file (drag-and-drop or file selection)
2. Enter search keyword
3. Choose search options:
   - Case sensitivity
   - Search algorithm
   - Regular expression
   - Fuzzy search threshold
4. Click "Search"

### 4. Viewing Results
- Results show:
  - Line numbers
  - Context around matches
  - Highlighted keywords
  - Search statistics
- Export options:
  - CSV format
  - Includes all match details

### 5. Search History
- View past searches
- Repeat previous searches
- Track search statistics
- Monitor performance

## Search Algorithms

### Boyer-Moore Algorithm
- Preprocesses pattern for efficient skipping
- Average-case complexity: O(n/m)
- Best for large texts and patterns

### Knuth-Morris-Pratt Algorithm
- Linear time complexity
- Uses failure function
- Good for repetitive patterns

### Fuzzy Search
- Levenshtein distance calculation
- Configurable threshold
- Finds similar words

### Wildcard Search
- * for multiple characters
- ? for single character
- Pattern matching

## File Processing

### PDF Files
- Text extraction using PyPDF2
- Preserves formatting
- Handles multiple pages

### Word Documents
- Text extraction using python-docx
- Preserves document structure
- Supports formatting

### Text Files
- Direct text processing
- Line-by-line analysis
- Efficient searching

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 