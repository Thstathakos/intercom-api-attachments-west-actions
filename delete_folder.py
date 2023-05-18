import os

# Get directory name
mydir = 'attachments'

# Try to remove the tree; if it fails, throw an error using try...except.
try:
    os.system('rmdir /S /Q "{}"'.format(mydir))
except OSError as e:
    print("Error: %s - %s." % (e.filename, e.strerror))
