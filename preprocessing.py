from file_class import File
import os
import configparser as ini_p
import regex as re
import regex_variables as revar
from importlib import reload
from pathlib import Path

import file_class
file_class = reload(file_class)


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
    config.read(base / "config.ini")

    # search strings
    search = {
        "tag_id": config['SEARCH STRINGS']['tag_id'],
    }

    # paths of folders
    paths = {
        "write_path": config['PATHS']['write_path'],
        "images_path": config['PATHS']['images_path']
    }

    # general options
    options = {
        "make_frontmatter": config['OPTIONS'].getboolean('generate_frontmatter'),
        "make_frontmatter_title": config['OPTIONS'].getboolean('frontmatter_title'),
        "make_frontmatter_tags": config['OPTIONS'].getboolean('frontmatter_tags'),
    }
    return search, paths, options


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
            appended = root / filename

            # If filename is a folder, check if it's in the
            # blacklist, and not then recursively search
            if (os.path.isdir(appended)):
                for x in IGNORE_DIRECTORIES:
                    if (appended == (base_root / x)):
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

def update_information_from_files(Directories):
    for File in Directories:
        File.reset_link_points()
    if INI_OPTIONS["make_frontmatter"] == True:
        if INI_OPTIONS["make_frontmatter_tags"] == True:
            for File in Directories:
                File.find_tags(INI_STRINGS["tag_id"])

    for File in Directories:
        File.find_tags(INI_STRINGS["tag_id"])
        File.the_big_sweeper()


def find_callback_file(Directories, search_string):
    for File in Directories:
        if search_string == str(File):
            return File
    raise Exception("No file found")


def parse_embeds(Directories):
    # Get embeds from each file
    for File in Directories:
        # Gets location of embeds to insert
        callbacks = File.the_big_parser()
        # print("callbacks: " + str(callbacks))

        # List of embed sections
        extracted_sections = []
        for callback in callbacks:
            # Get file that we want to search for
            embed_file = find_callback_file(Directories, callback["title"])
            # Get section of the file as a list of lines
            extracted_section = embed_file.find_section_in_file(
                callback["identifier"], callback["type"])
            
            # Append to list of embed sections
            extracted_sections.append({
                "section": extracted_section,
                "line": callback["line"]
                })
        
        # Reverse list (we need to go bottom to top to not overwrite
        # when inserting content into the list)
        extracted_sections.reverse()
        # Replace embed hyperlinks in the text with the embed sections
        for section in extracted_sections:
            File.replace_with_embed(section["section"], section["line"])

def parse_links(Directories):
    for File in Directories:
        print("@@@@@@@@@@@@@@")
        print("FILENAME: " + str(File))
        callbacks = File.the_big_wikilink_converter()
        # print("callbacks: " + str(callbacks))

        for callback in callbacks:
            # Get file that we want to search for
            embed_file = find_callback_file(Directories, callback["title"])
            # Get section of the file as a list of lines
            hyperlink_path = embed_file.path
            hyperlink_title = embed_file.title
            File.convert_link_to_md(hyperlink_path, hyperlink_title, callback)

def create_new_links(Directories, write_path):
    for File in Directories:
        new_path = write_path / Path(*File.path.parts[2:])
        File.path = new_path
    return


def write_to_files(Directories, write_path):
    for File in Directories:
        Path(File.path.parent).mkdir(parents=True, exist_ok=True)
        
        with open(File.path, "w") as f:
            for line in File.contents:
                f.write(line)
    return


BASE_DIR = Path("tests/vault")
IGNORE_DIRECTORIES = find_pyignore_file(BASE_DIR)
INI_STRINGS, INI_DIRS, INI_OPTIONS = ini_read(BASE_DIR)

directory = recursive_search(BASE_DIR)
# print(directory)

# for file in directory:
#     print(file)

# get_information_from_file("tests/vault/b/Abelian Group.md")
get_information_from_files(directory)

parse_embeds(directory)
update_information_from_files(directory)
create_new_links(directory, INI_DIRS["write_path"])
parse_links(directory)
write_to_files(directory, INI_DIRS["write_path"])

# for file in directory:
#     print("----------------")
#     print(file)
#     # print(repr(file))
