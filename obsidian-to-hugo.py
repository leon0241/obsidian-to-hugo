import os
import configparser as ini_p
import re

def find_ignore(root):
	for filename in os.listdir(root):
		if filename == ".py_ignore":
			f_append = root + "/" + filename
			with open(f_append, 'r') as f:
				text = f.readlines()
				return text
	return []


def ini_read(base):
	config = ini_p.ConfigParser()
	config.read(base + "/" + "config.ini")
	search = {
		"tag_id": config['SEARCH STRINGS']['tag_id']
	}
	options = {
		"gen_fm": config['OPTIONS'].getboolean('generate_frontmatter'),
		"fm_title": config['OPTIONS'].getboolean('frontmatter_title'),
		"fm_tags": config['OPTIONS'].getboolean('frontmatter_tags'),
	}
	return search, options


def recursive_search(root, base_root=None):
	'''
	Recursively searches a specified folder for markdown
	files, ignoring folders that are in .py_ignore
	'''

	directory_tuples = []

	# Messy shitty code

	# if no .pyignore
	if (IGNORE_DIRECTORIES == []):
		# For  each item in the root
		for filename in os.listdir(root):
			# Traverse 1 layer
			appended = root + "/" + filename

			# If filename is a folder, recursively search
			if (os.path.isdir(appended)):
				directory_tuples.append(recursive_search(appended))

			# If it's a markdown file then run function.
			elif (filename.endswith('.md')):
				print(filename)
				directory_tuples.append([appended, filename])
	else:
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
					directory_tuples.append(recursive_search(appended, root))

			# If it's a markdown file then run function.
			elif (filename.endswith('.md')):
				print(filename)
				directory_tuples.append([appended, filename])
	return directory_tuples

# func


def extract_lines(filename):
	extracted = open(filename, "r")
	return extracted.readlines()


def convert_file(filename):
	# flags (do all these at the end so loops don't mess up)
	flags = {
		"replace_fm": False,
		"fm_ending": 0,
		# random regex string i found online
		"title": re.search("(?:[^\\/](?!(\\|/)))+$", filename).group()[:-3],
		"tags": []
	}

	# extract lines and store in an array
	extracted = extract_lines(filename)

	# if there's frontmatter already, check where to replace it from
	if (extracted[0][:3] == "\'\'\'" and INI_OPTIONS["gen_fm"] == True):
		print("true")
		flags["replace_fm"] = True
		
		# get index of frontmatter end clause
		end_index = 1
		while True:
			# if it's a frontmatter, else go next line until
			if(extracted[end_index][:3] == "\'\'\'"):
				break
			else:
				end_index += 1
		flags["fm_ending"] = end_index
	
	# Searches first 10 lines, could be more but i'd imagine tags are at top
	for i in range(min(10, len(extracted))):
		# If string begins with the tag id
		if (extracted[i].startswith(INI_STRINGS["tag_id"])):
			# How many words to offset split
			lenz = len(INI_STRINGS["tag_id"].split())
			# Split tags into array and remove the tag_id
			flags["tags"] = extracted[i].split()[lenz:]

	print(flags)

BASE_DIR = "tests/vault"
IGNORE_DIRECTORIES = find_ignore(BASE_DIR)
INI_STRINGS, INI_OPTIONS = ini_read(BASE_DIR)

print(recursive_search(BASE_DIR))
convert_file("tests/vault/b/Abelian Group.md")