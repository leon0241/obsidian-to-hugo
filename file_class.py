import regex as re


class File:
    def __init__(self, title, path):
        self.title = title
        self.path = path
        tmpfile = open(self.path, "r").readlines()
        self.contents = tmpfile
        for i in range(len(tmpfile)-1):
            line = tmpfile[i]
            # print(line == "\n")
            self.contents[i] = line[:-1] if line != "\n" else line

        # print("--------------")
        # print(self.contents)
        # for i in range(len(self.contents)):
        #     print(self.contents[i])
        # self.contents = open(self.path, "r").readlines()

        self.tags = []

        self.contains_frontmatter = False

        self.header_sections = []
        self.block_sections = []

        self.checkpoints = {
            "frontmatter_end": 0,
            "tag_line": 0,
            "embeds": [],
        }

    def __str__(self):
        return self.title

    def __repr__(self):
        # return f'({self.title}, {self.path}, {self.tags})'
        return str(self.checkpoints["embeds"])

    def get_title(self):
        return self.title

    def find_frontmatter(self):
        '''
        Checks if there is frontmatter (so it will be replaced)

        Flags self.contains_frontmatter if it does
        Sets a checkpoint "frontmatter_end"
        '''

        if (self.contents[0][:3] == "\'\'\'"):
            self.contains_frontmatter = True
            print("true")

            # get index of frontmatter end clause
            end_index = 1
            while True:
                # if it's a frontmatter, else go next line until
                if (self.contents[end_index][:3] == "\'\'\'"):
                    break
                else:
                    end_index += 1
            self.checkpoints["frontmatter_end"] = end_index

    def find_tags(self, TAG_STRING):
        '''
        Finds the line that a tag occured in. This should only run if
        check for tags is true in the config.
        Returns an exception if a tag is not found
        '''

        # Searches first 10 lines, could be more but i'd imagine tags are at top
        # min to not overflow if there's less than 10 lines in a file
        for line in range(min(10, len(self.contents))):
            # If string begins with the tag id
            if (self.contents[line].startswith(TAG_STRING)):
                # How many words to offset split
                # e.g. if tag phrase was "Tags:" then length is 1
                # e.g. if tag phrase was "Tags here:" then length is 2
                tag_string_length = len(TAG_STRING.split())

                # Split tags into array (without the tag string)
                self.tags = self.contents[line].split()[tag_string_length:]
                self.checkpoints["tag_line"] = line
                return
        else:
            print("Warning: Tag was not found :/")
            return

    # def look_for_pattern(self, REGEX_PATTERN, current_index):
    #     search_pattern = None

    #     eof_index = len(self.contents) - 1

    #     while (search_pattern == None) and (current_index < eof_index):
    #         current_index += 1
    #         search_pattern = re.search(
    #             REGEX_PATTERN, self.contents[current_index])
    #     return current_index

    def look_for_headers(self, line, current_index):
        # "Non capture lookbehind between 1 and 6 '#' (indicates header)"
        # captures everything after that
        REGEX_HEADER = "^\#{1,6}\s.*"
        REGEX_HEADER_PRIO = "\#{1,6}"
        # does the line have a header or not
        does_line_have_header = re.search(REGEX_HEADER, line)
        # if it does have a header
        if does_line_have_header != None:
            header_title = does_line_have_header.group()
            title_hashes = re.search(REGEX_HEADER_PRIO, header_title).group()
            highest_header = len(title_hashes)
            # print("full header: " + header_title)
            # print("highest header: " + str(highest_header))
            header_title = header_title[highest_header:]
            # print("altered title: " + header_title)
            # set up variables for dictionary
            header_start = current_index
            # set up variables for loop
            search_result = None
            header_end = current_index
            eof_index = len(self.contents) - 1

            # while there isn't a next header, and
            while (search_result == None) and (header_end < eof_index):
                header_end += 1
                # print("line: " + self.contents[header_end])
                search_result = re.search(
                    REGEX_HEADER, self.contents[header_end])
                if search_result != None:
                    reg = re.search(REGEX_HEADER_PRIO, search_result.group())
                    if reg != None and len(reg.group()) > highest_header:
                        search_result = None
            # if terminated due to EOF then offset to not cut off section
            if header_end == eof_index:
                header_end += 1

            self.header_sections.append({
                "start": header_start,
                "end": header_end,
                "ref": header_title
            })
            # print("----------")
            # print("HEADERS")
            # print(self.header_sections)
            # print("----------")
        else:
            return

    def look_for_blocks(self, line, current_index):
        # "Non capture lookbehind between 1 and 6 '#' (indicates header)"
        # captures everything after that
        REGEX_BLOCK = "^\^.{1,6}$"
        REGEX_EMPTY = "^\s{0,}$"
        # does the line have a header or not
        does_line_have_block = re.search(REGEX_BLOCK, line)
        # if it does have a header
        if does_line_have_block != None:
            # set starting line variable
            block_end = current_index
            block_title = does_line_have_block.group()
            # loop continuously
            search_result = None
            block_start = current_index - 1
            # print(block_start)
            while (search_result == None) and (block_start > 0):
                block_start -= 1
                search_result = re.search(
                    REGEX_EMPTY, self.contents[block_start])

            self.block_sections.append({
                "start": block_start,
                "end": block_end - 1,
                "ref": block_title
            })
            # print("----------")
            # print("BLOCKS")
            # print(self.block_sections)
            # print("----------")
        else:
            return

    def get_section_contents(self):
        for section in self.header_sections:
            print("printing a section")
            subsection = self.contents[section["start"]:section["end"]]
            for i in subsection:
                print(i)
            # for i in range(section["start"], section["end"]):
            #     print(self.contents[i])

    def look_for_links(self, line, current_index):
        REGEX_LINK = "\[\[.*\]\]"
        REGEX_EMBED = "(?<=!\[\[).*(?=\]\])"
        REGEX_BLOCK = "#\^.{1,6}$"
        REGEX_HEADER = "#"  # lol
        REGEX_ALT = "\|"
        REGEX_IMAGE = "\.(png|jpg|svg|webp)"

        does_line_have_link = re.findall(REGEX_LINK, line)
        # if it does have a header
        if does_line_have_link != None:
            for link in does_line_have_link:
                # flags
                # check if file is embed or not
                is_embed = False
                does_line_have_embed = re.search(REGEX_EMBED, link)
                if does_line_have_embed != None:
                    is_embed = True
                    raw_text = does_line_have_embed.group()
                else:
                    raw_text = link[2:-2]

                link_type = ""
                if re.search(REGEX_BLOCK, raw_text) != None:
                    link_type = "block"
                elif re.search(REGEX_HEADER, raw_text) != None:
                    link_type = "header"
                elif re.search(REGEX_IMAGE, raw_text) != None:
                    link_type = "image"
                else:
                    link_type = "page"

                label = False
                if re.search(REGEX_ALT, raw_text) != None:
                    label = True
                self.checkpoints["embeds"].append({
                    "line": current_index,
                    "type": link_type,
                    "label": label,
                    "text": raw_text
                })
        else:
            return

    def the_big_sweeper(self):
        # print("--------------")
        # print("Title: " + self.title)
        # print(self.contents[0][-2])
        for i, line in enumerate(self.contents):
            # continue
            self.look_for_headers(line, i)
            self.look_for_blocks(line, i)
            self.look_for_links(line, i)
        self.get_section_contents()
