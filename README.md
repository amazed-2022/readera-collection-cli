# readera-collection-cli
An unofficial **command-line tool** for loading and exploring book and quote data from ReadEra backup file.

**License:** GNU GPL v3.0  
**Author:** amazed  
**Date:** Dec 2025  
[GitHub Repository](https://github.com/amazed-2022/collection/)


## Introduction
ReadEra is an excellent Android reading application, and this command-line tool exists solely to help users work with their own exported data outside the app.
If you enjoy using ReadEra, **please consider supporting the developers by purchasing the Premium version** in the official app.  

**This project is not affiliated with, endorsed by, or connected to ReadEra or its developers.**


## Installation
- **Create a backup file** in the ReadEra app (Settings / Backup & Restore)
- **Transfer backup file to your PC** (Google Drive, Gmail, etc.)
- **Unpack** `bak` file into a freely chosen folder (only `library.json` file will be needed, the rest can be deleted)
- **Simply download** `readera-collection-cli.py` next to your extracted `library.json` file
- **Open a Command prompt** (Press `Win + R`, type `cmd`) and navigate to the folder
- **Set window size** which is convenient (certain functions will be scaled to window width)
- **Run the script**  
  <img width="1202" height="192" alt="image" src="https://github.com/user-attachments/assets/04c30ea7-6f20-4644-8766-040bdec11f00" />

  
---
<img width="188" height="54" alt="image" src="https://github.com/user-attachments/assets/b1364046-8fae-43ea-bba9-fd4f6ca86627" />

To use all features of `readera-collection-cli`, the following should be ensured:
- Books should have **consistent, readable filenames**, e.g.:  
 `Example Author - Example Title.epub`
- Books should include an **Author** in the _About document_ page within the ReadEra app
- In the ReadEra app, books should be organized into **Collections** (which are basically folders), e.g. novels, sci-fi, etc.
- After finishing a book, it should be **marked as "Have read"** in the ReadEra app
  <img width="540" height="440" alt="image" src="https://github.com/user-attachments/assets/43643fec-3896-44d8-b2c4-44ab0a7556a0" />
- Books should include a text-based **Review** in the _About document_ page, containing the following data, **separated by semicolons**:  
 `publish date`;`rating`;`ratings count`;  
  <img width="539" height="166" alt="image" src="https://github.com/user-attachments/assets/abfad442-21f4-408e-8eef-743eeb6ef722" />  
  (I use data from [goodreads](https://www.goodreads.com/))


## Features / Highlights
### Menu-Driven Navigation
- Easy-to-use  menu with numbered options  
- Exit with the “x” option

  <img width="323" height="217" alt="image" src="https://github.com/user-attachments/assets/5cec33f0-cc0e-43c7-8bf8-5f121967d103" />

### Random quote prints
In these functions, user can hit any key for more quotes or input `x` for exit

-  1  -->  Print random quotes from the entire Collection
-  2  -->  Print random quotes from a selected Author
-  3  -->  Print random quotes from a selected Folder

### Book based exploration
-  4  -->  View and export all quotes from a specific book (a `txt` file will be created in the working folder)
-  5  -->  See quote distribution within a book (x axis: pages, y axis: quote text length distribution)
        <img width="770" height="376" alt="image" src="https://github.com/user-attachments/assets/5c440382-ea0d-46a6-a012-8627cc0a732c" />  
-  6  -->  List books by specific properties  
  - added on (basically the file modified time)
  - reading now (books currently to **Reading Now** section)
  - finished list (books already marked as **Have Read**)
  - read duration (first inserted quote data - **Have Read** date)
  - publish date (extracted from the text-based **Review** of the books)
  - number of quotes
  - quote/page ratio
  - rating (extracted from the text-based **Review** of the books)
  - folder (user specific **Collections**, aka Folders)

### Statistics (option 7)
Analyze your collection for insights and summary data

### Search (option 8)
Search quotes across the collection using keywords



## License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  
Copyright (C) amazed 2025.

This software is free to use, modify, and distribute under the terms of the GPL-3.0.  
You should have received a copy of the GNU General Public License along with this program.  
If not, see [GPL-3.0 License](https://www.gnu.org/licenses/gpl-3.0.html).
