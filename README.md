# Curses-PDF-Merger
This software is built towards easily merging PDF files. It has a nice TUI made with the Python with Curses library with the goal of providing an easy interface towards merging PDFs. I want to try and make it generate header files with Tex in the near future so it can generate header files. I typically use this software for lab, where I have to make header files, and merge different PDFs together such as schematics, questions and answers, and other things. Maybe you'll find something helpful here too!

# To-do
Make sure the files are valid PDFs. File extensions are not enough. Use pypdf to read, and if it throws an exception, assume it's an invalid PDF.
Secondly, when you jump straight into compile mode (for some reason back then it didn't let you do that when you try to jump from navigate -> compile) make sure that it deletes directories properly.
