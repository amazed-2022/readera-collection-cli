# readera-collection-cli
An unofficial **command-line tool** for loading and exploring book and quote data from ReadEra backup files.

**License:** GNU GPL v3.0  
**Author:** amazed  
**Date:** Dec 2025  
[GitHub Repository](https://github.com/amazed-2022/collection/)


## Introduction
ReadEra is an excellent Android reading application, and this command-line tool exists solely to help users work with their own exported data outside the app.  
If you enjoy using ReadEra, **please consider supporting the developers by purchasing the Premium version** in the official app.  

**This project is not affiliated with, endorsed by, or connected to ReadEra or its developers.**


## Features / Highlights

To use all features of `readera-collection-cli`, the following should be ensured:
- Books should have **consistent, readable filenames**, e.g.:  
 `Example Author - Example Title.epub`
- Books should include an **Author** in the _About document_ page within the ReadEra app
- Books should include a text-based **Review** in the _About document_ page, containing the following data, **separated by semicolons**:  
 `publish date`;`rating`;`ratings count`;
- In the ReadEra app, books should be organized into **Collections** (which are basically folders), e.g. novels, sci-fi, etc.
- After finishing a book, it should be **marked as "Have read"** in the ReadEra app

### Menu-Driven Navigation
- Easy-to-use  menu with numbered options  
- Exit with the “x” option

  <img width="317" height="219" alt="image" src="https://github.com/user-attachments/assets/6aaba109-a2f8-400f-9e0a-4857c32419a3" />


### Random Quote prints (option 1-3)
- Print random quotes from the entire collection
- Print random quotes from a selected author
- Print random quotes from a selected folder


### Book-Based Exploration (option 4-6)
- View and export all quotes from a specific book
- See quote distribution within a book
- List books by specific properties
  - added on
  - reading now
  - finished list
  - read duration
  - publish date
  - number of quotes
  - quote/page ratio
  - rating
  - folder

### Statistics (option 7)
Analyze your collection for insights and summary data

### Search (option 8)
Search quotes across the collection using keywords


## Installation
- Simply download `collection.py` next to your extracted `library.json` file.
- Open a Command prompt (Press `Win + R`, type `cmd`) and navigate to the folder  
- Run the script  
  <img width="1202" height="192" alt="image" src="https://github.com/user-attachments/assets/04c30ea7-6f20-4644-8766-040bdec11f00" />



## License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
Copyright (C) amazed 2025.

This software is free to use, modify, and distribute under the terms of the GPL-3.0.  
You should have received a copy of the GNU General Public License along with this program.  
If not, see [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).
