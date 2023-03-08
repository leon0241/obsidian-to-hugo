import os

def find_ignore(root):
    for filename in os.listdir(root):
        if filename == ".py_ignore":
            f_append = root + "/" + filename
            with open(f_append, 'r') as f:
                text = f.readlines()
                return text
    return []

IGNORE_DIRECTORIES = find_ignore("tests/vault")

def recursive_search(root):
    '''
    Recursively searches a specified folder for markdown
    files, ignoring folders that are in .py_ignore
    '''
    
    # Messy shitty code
    if (IGNORE_DIRECTORIES == []):
        search_no_blacklist(root)
    else:
        search_blacklist(root)

def search_no_blacklist(root):
    '''Searches in the case there is no .py_ignore'''
    
    # For  each item in the root
    for filename in os.listdir(root):
        # Traverse 1 layer
        appended = root + "/" + filename
    
        # If filename is a folder, recursively search
        if (os.path.isdir(appended)):
            recursive_search(appended)
        
        # If it's a markdown file then run function. 
        elif (filename.endswith('.md')):
            print(filename)
            # append_eof(appended)

def search_blacklist(root):
    '''Searches in the case there is a py_ignore'''
    
    # For  each item in the root
    for filename in os.listdir(root):
        # Traverse 1 layer
        appended = root + "/" + filename
    
        # If filename is a folder, check if it's in the
        # blacklist, and not then recursively search
        if (os.path.isdir(appended)):
            for x in IGNORE_DIRECTORIES:
                if (filename == x):
                    break
            # Somehow this is valid syntax :D
            else:
                recursive_search(appended)
        
        # If it's a markdown file then run function. 
        elif (filename.endswith('.md')):
            print(filename)
            # append_eof(appended)

def append_eof(filename):
    with open(filename, 'r+') as f:
        text = f.readlines()
        if (text == []):
            return

    if (text[-1] != "%%EOF%%"):
        f.write("\n%%EOF%%")

print(appended in x for x in IGNORE_DIRECTORIES)

recursive_search("tests/vault")