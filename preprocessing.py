import os
import configparser as ini_p
import re
import regex_variables as revar
from importlib import reload

import file_class
file_class = reload(file_class)
from file_class import File

def find_pyignore_file(root):
    '''
    Attempts to find a .py_ignore file
    '''
    
    # for each file in the root of the destination
    for filename in os.listdir(root):
        # if said filename is .py_ignore then
        if filename == ".py_ignore":
            # get correct file location
            f_append = root + "/" + filename

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
        "tag_id": config['SEARCH STRINGS']['tag_id']
    }

    # general options
    options = {
        "make_frontmatter": config['OPTIONS'].getboolean('generate_frontmatter'),
        "make_frontmatter_title": config['OPTIONS'].getboolean('frontmatter_title'),
        "make_frontmatter_tags": config['OPTIONS'].getboolean('frontmatter_tags'),
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

def extract_lines(filename):
    extracted = open(filename, "r")
    return extracted.readlines()

def get_information_from_file(Directories):
    if INI_OPTIONS.make_frontmatter == True:
        for File in Directories:
            File.find_frontmatter()
    
        if INI_OPTIONS.make_frontmatter_tags == True:
            for File in Directories:
                File.find_tags(INI_STRINGS["tag_id"])

    for File in Directories:
        File.the_big_sweeper()


# def convert_file(filename):
#     # flags (do all these at the end so loops don't mess up)
#     flags = {
#         "replace_fm": False,
#         "fm_ending": 0,
#         # random regex string i found online
#         "title": re.search("(?:[^\\/](?!(\\|/)))+$", filename).group()[:-3],
#         "tags": []
#     }

#     # extract lines and store in an array
#     extracted = extract_lines(filename)

#     # if there's frontmatter already, check where to replace it from
#     if (extracted[0][:3] == "\'\'\'" and INI_OPTIONS["gen_fm"] == True):
#         print("true")
#         flags["replace_fm"] = True
        
#         # get index of frontmatter end clause
#         end_index = 1
#         while True:
#             # if it's a frontmatter, else go next line until
#             if(extracted[end_index][:3] == "\'\'\'"):
#                 break
#             else:
#                 end_index += 1
#         flags["fm_ending"] = end_index
    
#     # Searches first 10 lines, could be more but i'd imagine tags are at top
#     for i in range(min(10, len(extracted))):
#         # If string begins with the tag id
#         if (extracted[i].startswith(INI_STRINGS["tag_id"])):
#             # How many words to offset split
#             lenz = len(INI_STRINGS["tag_id"].split())
#             # Split tags into array and remove the tag_id
#             flags["tags"] = extracted[i].split()[lenz:]

#     extracted = search_links(extracted)
#     print(flags)

# def search_links(extracted, directory):
#     for i, line in enumerate(extracted):
#         link_search = re.search("\[\[.*\]\]", line)
#         # then it found a link in the line
#         if link_search != None:
#             SECTION_SEARCH = "\[\[.*\#\^.*\]\]"
#             HEADING_SEARCH = "\[\[.*\#.*\]\]"
#             EMBED_SEARCH = "\!\[\[.*\]\]"
#             SECTION_TITLE = "(?<=\[\[).*(?=\#)"
#             REGULAR_TITLE = "(?<=\[\[).*(?=\]\])"


BASE_DIR = "tests/vault"
IGNORE_DIRECTORIES = find_pyignore_file(BASE_DIR)
INI_STRINGS, INI_OPTIONS = ini_read(BASE_DIR)

directory = recursive_search(BASE_DIR)
print(directory)

for file in directory:
    print(file)

get_information_from_file("tests/vault/b/Abelian Group.md")