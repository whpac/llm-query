from datetime import datetime
from hashlib import md5
import json
import os
import re
import time
from clients import createClient, AVAILABLE_MODELS
from utils.args import getArguments
import utils.magic_words as magicWords


def main():
    args = getArguments(AVAILABLE_MODELS)

    if args.dryRun:
        print('Dry run mode: no requests will be sent to the LLM')

    with open(args.inputFile, 'r', encoding='utf-8') as file:
        inputData = json.load(file)

    # If we're told to write to an already existing file, append to it
    # instead of overwriting it
    outputData = []
    if args.outputFile.endswith('.json') and os.path.exists(args.outputFile):
        with open(args.outputFile, 'r', encoding='utf-8') as file:
            outputData = json.load(file)

    # By default, continue from the last entry in the output file
    skipEntries = args.skip if args.skip is not None else len(outputData)
    inputData = inputData[skipEntries:]
    if args.limit:
        inputData = inputData[:args.limit]

    dumpsDir = os.path.abspath(args.dumps)
    dumpsDir = os.path.join(dumpsDir, datetime.now().strftime('%Y-%m-%d'))
    if not args.dryRun:
        os.makedirs(dumpsDir, exist_ok=True)

    llmClient = createClient(args.model, args.apiKey)
    print(f'Processing {len(inputData)} entries, starting at {skipEntries+1}\n')

    try:
        for i, entry in enumerate(inputData):
            # Default identifiers: entry_00001 etc. (starting from 1)
            entryId = entry.get('id', f'entry_{i+1:05}')
            entry['id'] = entryId
            print(f'\033[1A\rProcessing entry {i+1}/{len(inputData)} ({entryId})\033[K')

            entryResult = {}
            try:
                if 'promptText' not in entry:
                    raise Exception(f'Prompt text is missing in entry `{entryId}`. Skipping!')

                promptText = entry['promptText']
                promptText = expandDynamicContent(promptText, entryId)
                if args.print:
                    print(f'== {entryId} ==\n{promptText}\n\n\n')

                dumpFile = makeFileNameForResponseDump(dumpsDir, entryId)
                if not args.dryRun:
                    response = llmClient.ask(promptText)
                    with open(dumpFile, 'w', encoding='utf-8') as file:
                        json.dump(response.__dict__, file, indent=4)

                entryResult['success'] = True
                entryResult['dump'] = dumpFile
            except Exception as e:
                entryResult['success'] = False
                entryResult['error'] = str(e)
                print(f'Error processing prompt `{entryId}`: {e}\n')
            entry['result'] = entryResult
            outputData.append(entry)
            time.sleep(args.delay)

    except KeyboardInterrupt:
        print('Process interrupted by the user. Saving progress...')
    finally:
        with open(args.outputFile, 'w', encoding='utf-8') as file:
            json.dump(outputData, file, indent=4)


def makeFileNameForResponseDump(dumpsDir, entryId):
    # Don't use colon here, it has special meaning in paths
    now = datetime.now().strftime('%Y-%m-%dT%H.%M.%S')
    entryId = re.sub(r'[/\\<:>"|?*]', '_', entryId)

    if len(entryId) > 100:
        # For long entry ids, ensure we don't exceed the filesystem path length limit
        dumpFile = f'llm-{entryId[:80]}-{md5(entryId.encode()).hexdigest()}-{now}.json'
    else:
        dumpFile = f'llm-{entryId}-{now}.json'
    
    dumpFile = os.path.join(dumpsDir, dumpFile)
    dumpFile = os.path.abspath(dumpFile)
    return dumpFile


def expandDynamicContent(promptText, entryId):
    def expandMagicWord(regexMatch):
        magicWord = regexMatch.group(1).lower()
        params = None
        if regexMatch.group(2):
            params = regexMatch.group(2).strip()

        magicWordFunc = getattr(magicWords, magicWord, None)
        if magicWordFunc is None:
            print(f'Unrecognized magic word `#{magicWord}` in entry `{entryId}`.\n')
        elif not callable(magicWordFunc):
            print(f'Warning: `#{magicWord}` (entry `{entryId}`) is not callable.\n')
        else:
            try:
                replacement = magicWordFunc(params)
                if replacement is not None:
                    return replacement
            except Exception as e:
                print(f'Error when calling magic word `#{magicWord}` in entry `{entryId}`: {e}\n')

        return regexMatch.group(0)
    return re.sub(r'{{#(\w+)(?::(.*?))?}}', expandMagicWord, promptText, flags=re.I)


def includeFilesInPrompt(promptText):
    files = re.findall(r'({{#include:(.+?)}})', promptText)
    for placeholder, filePath in files:
        with open(filePath, 'r', encoding='utf-8') as file:
            replacement = file.read()
        promptText = promptText.replace(placeholder, replacement)
    return promptText


main()