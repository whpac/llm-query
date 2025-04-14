import argparse
import json
from os.path import join, dirname, abspath, normpath, exists

def getArguments(availableModels):
    parser = argparse.ArgumentParser(description='Reads a list of ready prompts and asks them to the LLM')
    parser.add_argument('inputFile', type=str, help='JSON file containing description of prompts')
    parser.add_argument('outputFile', type=str, help='Output JSON file with references to chat dumps')
    parser.add_argument('--dumps', type=str, help='Root directory where to store chat dumps', default=None)
    parser.add_argument('-s', '--skip', type=int, help='Skip the first N prompts', default=None)
    parser.add_argument('-l', '--limit', type=int, help='Limit the number of prompts to process', default=None)
    parser.add_argument('-m', '--model', type=str, help='Model to use for the LLM', choices=availableModels, default=None)
    parser.add_argument('-d', '--delay', type=int, help='Delay between requests to the LLM', default=None)
    parser.add_argument('-c', '--config', type=str, help='JSON file with configuration options', default=None)
    parser.add_argument('-a', '--apiKey', type=str, help='API key for the LLM', default=None)
    parser.add_argument('--dryRun', action='store_true', help='Do not send requests to the LLM, just process the prompts')
    parser.add_argument('--print', action='store_true', help='Print the prompts to the console')
    args = parser.parse_args()

    try:
        if args.config:
            configFile = abspath(args.config)
            args = readArgumentsFromFile(configFile, args)
            delattr(args, 'config') # We no longer need it after this point

        validateArgs(args, availableModels)
    except ValueError as e:
        parser.error(str(e))

    if args.dumps is None:
        args.dumps = './dumps'
    if args.delay is None:
        args.delay = 4

    return args


def readArgumentsFromFile(filePath, baseArgs, appliedFiles=[]):
    """
    Reads a JSON configuration file and updates the baseArgs object with the values from the file.
    It supports extending other configuration files using the `$extends` key.
    The `$extends` key can be used to include other configuration files, allowing for
    a hierarchical configuration structure.
    The function only updates the attributes of baseArgs that are not already set to a
    value (other than None or False). Only keys that are present in baseArgs are considered valid.
    If an unknown key is encountered, a ValueError is raised.
    """
    if not exists(filePath):
        raise FileNotFoundError(f'Configuration file `{filePath}` not found')
    if filePath in appliedFiles:
        raise ValueError(f'A loop detected in configuration. `{filePath}` is already applied')
    
    baseFilePath = None
    appliedFiles.append(filePath)
    with open(filePath, 'r', encoding='utf-8') as file:
        config = json.load(file)
        for key, value in config.items():
            if key == '$extends':
                baseFilePath = normpath(join(dirname(filePath), value))
            elif not hasattr(baseArgs, key):
                raise ValueError(f'Unknown configuration option: {key} in file `{filePath}`')
            elif getattr(baseArgs, key) in [ None, False ]:
                setattr(baseArgs, key, value)

    # This is applied after the current file so that the base file cannot override the current file
    if baseFilePath is not None:
        baseArgs = readArgumentsFromFile(baseFilePath, baseArgs, appliedFiles)

    return baseArgs


def validateArgs(args, availableModels):
    if args.model is None:
        raise ValueError('You must specify a model to use for the LLM')
    if args.model not in availableModels:
        raise ValueError(f'Unsupported model: {args.model}')
    if args.apiKey is None:
        raise ValueError('You must specify an API key for the LLM')
