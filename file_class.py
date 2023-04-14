class File:
    def __init__(self, title, path):
        self.title = title
        self.path = path

        self.tags
        
        self.contains_frontmatter = False
        self.checkpoints = {
            "frontmatter_end": 0,

        }
        
        self.contents = open(self.path, "r").readlines()
        
    def __str__(self):
        return self.title
    
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
                if(self.content[end_index][:3] == "\'\'\'"):
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
            if (self.contents[line].startswith(TAG_STRING["tag_id"])):
                # How many words to offset split
                # e.g. if tag phrase was "Tags:" then length is 1
                # e.g. if tag phrase was "Tags here:" then length is 2
                tag_string_length = len(TAG_STRING["tag_id"].split())

                # Split tags into array (without the tag string)
                self.tags = self.contents[line].split()[tag_string_length:]
                return
        else:
            print("Warning: Tag was not found :/")
            return