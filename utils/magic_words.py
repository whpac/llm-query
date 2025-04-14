# In this file you can define functions that support any magic words
# you want to use in your prompts.
# 
# Magic word is a construct in double curly braces that start with a hash sign, for example:
#        {{#magicWord:param}}
# Magic words can be also invoked without parameters, like this:
#        {{#magicWord}}    or    {{#magicWord:}}
#
# The first part is the magic word name. It must be a valid Python function name. If a function
# with this name is defined in this file, it will be invoked to generate the content.
# After the magic word name, you can specify an optional parameter. The parameter value is not
# parsed, and is passed as-is as the first argument to the function.
#
# This file defines a single exemplary magic word, `#include`, which includes the content of a file.
# It may be used as follows:
#        {{#include:path/to/file.txt}}
# The content of the file will be inserted in place of the magic word.
#
# Functions for magic words should always accept a single argument, which is the parameter value.
# Even if the parameter is not used, it should be present in the function signature.
# The function should return a string, which will be inserted in place of the magic word.
# If you need to accept multiple parameters, you will need to parse by yourself the string
# passed as the only parameter.
# If you return None or throw an exception, the magic word will not be replaced, and the original
# text will be kept in place.

def include(filePath):
    with open(filePath, 'r', encoding='utf-8') as file:
        return file.read()
