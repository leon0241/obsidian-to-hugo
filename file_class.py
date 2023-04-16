import regex as re


class File:
    """Represents a markdown file and related information.

    Contains information about the lines of where/when links, embeds appear
    so it will be able to be cross referenced when parsing embeds.

    Attributes:
        title: The title of the document
        path: File path to the document fron root
        contents: Contents of the file. Stored line by line in a list
        tags: List of tags in the document header
        contains_frontmatter: Whether pre-existing frontmatter is there
        header_sections: List of headers and header sections in the file
        block_sections: List of blocks and block sections in the file
        embeds: List of links/embeds and related information in the file
        checkpoints: Dict of important line numbers
    """

    def __init__(self, title, path):
        """Initialises the class based on the title and file path

        Args:
            title: The title of the document
            path: File path to the document from root
        """

        self.title = title

        self.path = path
        # opens file for reading
        tmpfile = open(self.path, "r").readlines()
        self.contents = tmpfile
        # every line has a \n, except the last one
        for i in range(len(tmpfile)-1):
            line = tmpfile[i]
            # if the line is blank then leave it
            self.contents[i] = line[:-1] if line != "\n" else line

        self.tags = []

        self.contains_frontmatter = False

        self.header_sections = []
        self.block_sections = []
        self.links = []

        self.checkpoints = {
            "frontmatter_end": 0,
            "tag_line": 0,
        }

    def __str__(self):
        return self.title

    def __repr__(self):
        # return f'({self.title}, {self.path}, {self.tags})'
        return str(self.header_sections) +"\n"+str(self.block_sections)
        return str(self.embeds)

    def find_frontmatter(self):
        """Checks if there is frontmatter. Gets end line of pre-existing frontmatter if so.

        Args:
            None
        Returns:
            self.checkpoints["frontmatter_end"]: updated to the end line
        """

        if (self.contents[0][:3] == "\'\'\'"):
            self.contains_frontmatter = True

            # get index of frontmatter end clause
            end_index = 1
            while True:
                # if it's a frontmatter, else go next line
                if (self.contents[end_index][:3] == "\'\'\'"):
                    break
                else:
                    end_index += 1
            self.checkpoints["frontmatter_end"] = end_index

    def find_tags(self, TAG_STRING):
        """Finds if tags are present, and if so what line they are on. Should only run if checks for tags is true in config. 

        Args:
            TAG_STRING: Custom tag key phrase to search for

        Updates:
            self.tags: List of tag names
            self.checkpoints["tag_line"]: line that the tags are on
        
        Raises:
            Prints a warning if no tags are found
        """

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

    def look_for_headers(self, line, current_index):
        """Finds header tags in a line, and the block it represents in the text.

        Args:
            line: File contents to parse
            current_index: Line number to start from

        Returns:
            self.header_sections: Creates a header reference. Appends list of type:
            {start, end, ref}: start line, end line, header name
        """

        REGEX_HEADER = "^\#{1,6}\s.*"   # 1-6 "# [some text]"
        REGEX_HEADER_PRIO = "\#{1,6}"   # 1-6 "#"

        # does the line have a header or not
        does_line_have_header = re.search(REGEX_HEADER, line)
        # if it does have a header
        if does_line_have_header != None:
            header_title = does_line_have_header.group()
            
            # How many hashtags are in the header
            highest_header = len(
                re.search(REGEX_HEADER_PRIO, header_title).group())
            # Offset the hashtags
            header_title = header_title[highest_header:]

            # set up variables for dictionary
            header_start = current_index
            # set up variables for loop
            search_result = None
            header_end = current_index
            eof_index = len(self.contents) - 1

            # search down through each line until finds header/eof
            while (search_result == None) and (header_end < eof_index):
                header_end += 1
                # search for header
                search_result = re.search(
                    REGEX_HEADER, self.contents[header_end])
                # if header is found, check the header isn't lower ranked
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
        else:
            return

    def look_for_blocks(self, line, current_index):
        """Finds block tags in a line, and the block it represents in the text.

        Args:
            line: File contents to parse
            current_index: Line number to start from

        Updates:
            self.block_sections: Creates a block refernece. Appends dict of type:
            {start, end, ref}: start line, end line, header name
        """

        REGEX_BLOCK = "^\^.{6}$"  # "^"" followed by 6 characters
        REGEX_EMPTY = "^\s{0,}$"    # Empty line
        
        # does the line have a header or not, and if yes
        does_line_have_block = re.search(REGEX_BLOCK, line)
        if does_line_have_block != None:
            # set starting line variable
            block_end = current_index
            # title is the reference e.g. "^10256a"
            block_title = does_line_have_block.group()
            
            # set up variables for loop
            search_result = None
            block_start = current_index - 1

            # search up through each line until finds an empty line
            while (search_result == None) and (block_start > 0):
                block_start -= 1
                search_result = re.search(
                    REGEX_EMPTY, self.contents[block_start])

            self.block_sections.append({
                "start": block_start,
                "end": block_end - 1,
                "ref": block_title
            })
        else:
            return

    def get_section_contents(self):
        # wip
        for section in self.header_sections:
            subsection = self.contents[section["start"]:section["end"]]

    def look_for_links(self, line, current_index):
        """
        Finds links in a line. Gets type, whether it is an embed, and whether it has alt text.

        Args:
            line: File contents to parse
            current_index: Line number to start from

        Updates:
            self.links: Update a link reference. Appends dict of type:
            {
                line: index of line
                is_embed: bool - is it an embed or not
                type: can be "block", "header", "image", "page"
                label: whether there is alt text
                text: contents of the link
            }
        """

        REGEX_LINK = "!?\[\[.*\]\]"             # 0/1"!" + "[["+text+"]]"
        REGEX_EMBED = "(?<=!\[\[).*(?=\]\])"    # "![[" text "]]" (get text)
        REGEX_BLOCK = "#\^.{6}$"                # "^" followed by 6 chars
        REGEX_HEADER = "#"                      # "#" lol
        REGEX_ALT = "\|"                        # "|" lol 2 
        REGEX_IMAGE = "\.(png|jpg|svg|webp)"    # . followed by a file ext.

        # does line have a header, and if it does
        does_line_have_link = re.findall(REGEX_LINK, line)
        if does_line_have_link != None:
            for link in does_line_have_link:
                # big flag chain
                # check if link is an embed or not
                is_embed = False
                # print("link:" + link)
                does_line_have_embed = re.search(REGEX_EMBED, link)
                # print("e: " + str(does_line_have_embed))
                # if yea then raw text is the regex, otherwise strip the [[]]
                if does_line_have_embed != None:
                    is_embed = True
                    raw_text = does_line_have_embed.group()
                else:
                    raw_text = link[2:-2]

                # check link type (block/header/image/full page)
                link_type = ""
                if re.search(REGEX_BLOCK, raw_text) != None:
                    link_type = "block"
                elif re.search(REGEX_HEADER, raw_text) != None:
                    link_type = "header"
                elif re.search(REGEX_IMAGE, raw_text) != None:
                    link_type = "image"
                else:
                    link_type = "page"

                # check if link has alt text or not
                label = False
                if re.search(REGEX_ALT, raw_text) != None:
                    label = True
                
                self.links.append({
                    "line": current_index,
                    "is_embed": is_embed,
                    "type": link_type,
                    "label": label,
                    "text": raw_text
                })
        else:
            return

    def find_section_in_file(self, reference, type):
        REGEX_LINK = "(?<=!?\[\[).*(?=\]\])"
        REGEX_ALT = "\|"
        
        if type == "block":
            for block in self.block_sections:
                print("----------------")
                clean_block = block["ref"]
                print("block ref: " + clean_block)
                
                if clean_block == reference:
                    print("FOUND")
                    return block
            return
        elif type == "header":
            for header in self.header_sections:
                print("----------------")
                clean_header = re.search(REGEX_LINK, header["ref"])
                if clean_header != None:
                    print("original title: " + header["ref"])
                    clean_header = clean_header.group()
                    if re.search(REGEX_ALT, clean_header) != -1:
                        clean_header = clean_header.replace("|", " ", 1)
                        print(clean_header)
                else:
                    clean_header = header["ref"]
                print("header ref: " + clean_header)
                
                if clean_header == reference:
                    print("FOUND")
                    return header
            return
        elif type == "page":
            print("FOUND")
            return

    def the_big_sweeper(self):
        '''Iterate over every line finding headers, blocks, and links

        Args:
            None
        Updates:
            self.header_sections: headers and the sections they represents
            self.block_sections: blocks and the sections they represents
            self.links: link types and whether it is an embed or has alt text
        '''

        for i, line in enumerate(self.contents):
            self.look_for_headers(line, i)
            self.look_for_blocks(line, i)
            self.look_for_links(line, i)
        self.get_section_contents()
    
    def the_big_parser(self):
        REGEX_PURE_TITLE = ".*(?=#|\|)"
        REGEX_ID_BLOCK = "(?<=#)\^.{6}"
        REGEX_ID_HEADER = "(?<=#).*"
        
        callbacks = []
        # print("----------------")
        # print("title: " + self.title)
        # print("links: " + str(self.links))
        for link in self.links:
            if link["is_embed"] and link["type"] != "image":
                raw_text = link["text"]
                if link["type"] != "page" or link["label"]:
                    raw_text = re.search(REGEX_PURE_TITLE, raw_text).group()
                
                identifier = link["text"]
                if link["type"] == "block":
                    identifier = re.search(REGEX_ID_BLOCK, link["text"]).group()
                elif link["type"] == "header":
                    identifier = re.search(REGEX_ID_HEADER, link["text"]).group()
                
                callbacks.append({
                    "title": raw_text,
                    "identifier": identifier,
                    "type": link["type"]
                    })
        
        return callbacks

        