import os
import configparser as ini_p
import regex as re
import regex_variables as revar
from importlib import reload

import file_class
file_class = reload(file_class)
from file_class import File

def find_pyignore_file(root):
    '''
    Attempts to find a .py_ignore file
    '''
    
    # TODO: use pathlib library
    # https://medium.com/@ageitgey/python-3-quick-tip-the-easy-way-to-deal-with-file-paths-on-windows-mac-and-linux-11a072b58d5f

    # for each file in the root of the destination
    for filename in os.listdir(root):
        # if said filename is .py_ignore then
        if filename == ".py_ignore":
            # get correct file location
            f_append = os.path.join(root, filename)

            # open file and store the values in an array, return
            with open(f_append, 'r') as f:
                text = f.readlines()
                return text
    # else return empty array
    return []

def ini_read(base):
    '''
    Parses a config.ini file into a readable dictionary.
    These are configuration options of the file
    '''
    
    # initialise config parse
    config = ini_p.ConfigParser()
    # read file
    config.read(base + "/" + "config.ini")
    
    # search strings
    search = {
        "tag_id": config['SEARCH STRINGS']['tag_id'],
    }

    # general options
    options = {
        "make_frontmatter": config['OPTIONS'].getboolean('generate_frontmatter'),
        "make_frontmatter_title": config['OPTIONS'].getboolean('frontmatter_title'),
        "make_frontmatter_tags": config['OPTIONS'].getboolean('frontmatter_tags'),

        "images_path": config['OPTIONS']['images_path']
    }
    return search, options

def create_file_class(file_path, file_name):
    # remove ".md" from filename
    name_no_ext = file_name[:-3]
    NewClass = File(name_no_ext, file_path)
    return NewClass

def recursive_search(root, base_root=None):
    '''
    Recursively searches a specified folder for markdown
    files, ignoring folders that are in .py_ignore
    '''
    
    # List of "File" classes
    Directories = []

    # Messy shitty code

    # if no .pyignore
    if (IGNORE_DIRECTORIES == []):
        # For  each item in the root
        for filename in os.listdir(root):
            # Traverse 1 layer
            appended = root + "/" + filename

            # If filename is a folder, recursively search
            if (os.path.isdir(appended)):
                NewClass = create_file_class(appended, filename)
                Directories.extend(NewClass)

            # If it's a markdown file then run function.
            elif (filename.endswith('.md')):
                NewClass = create_file_class(appended, filename)
                Directories.append(NewClass)
    else:
        # If the base root isn't provided (it will for recursive)
        # then set the base root to the root
        if base_root == None:
            base_root = root

        # For  each item in the root
        for filename in os.listdir(root):
            # Traverse 1 layer
            appended = root + "/" + filename

            # If filename is a folder, check if it's in the
            # blacklist, and not then recursively search
            if (os.path.isdir(appended)):
                for x in IGNORE_DIRECTORIES:
                    if (appended == (base_root + "/" + x)):
                        break
                # Somehow this is valid syntax :D
                else:
                    Directories.extend(recursive_search(appended, root))

            # If it's a markdown file then run function.
            elif (filename.endswith('.md')):
                NewClass = create_file_class(appended, filename)
                Directories.append(NewClass)
    return Directories

def get_information_from_files(Directories):
    if INI_OPTIONS["make_frontmatter"] == True:
        for File in Directories:
            File.find_frontmatter()
    
        if INI_OPTIONS["make_frontmatter_tags"] == True:
            for File in Directories:
                File.find_tags(INI_STRINGS["tag_id"])

    for File in Directories:
        File.the_big_sweeper()

def find_callback_file(Directories, search_string):
    for File in Directories:
        if search_string == str(File):
            return File
    raise Exception("No file found")

def parse_files(Directories):
    for File in Directories:
        callbacks = File.the_big_parser()
        print("callbacks: " + str(callbacks))
        for callback in callbacks:
            embed_file = find_callback_file(Directories, callback["title"])
            print()
            print("@@@@@@@@@@@@@@@@@@@@@")
            print("file to look in: " + str(embed_file))
            embed_file.find_section_in_file(callback["identifier"], callback["type"])

BASE_DIR = "tests/vault"
IGNORE_DIRECTORIES = find_pyignore_file(BASE_DIR)
INI_STRINGS, INI_OPTIONS = ini_read(BASE_DIR)

directory = recursive_search(BASE_DIR)
# print(directory)

# for file in directory:
#     print(file)

# get_information_from_file("tests/vault/b/Abelian Group.md")
get_information_from_files(directory)

parse_files(directory)

# for file in directory:
#     print("----------------")
#     print(file)
#     # print(repr(file))