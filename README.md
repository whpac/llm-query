# LLM query tool

This repository contains a Python script that can be used for batch querying Large Language Models.

## Usage

The script `ask_llm.py` expects that you have a JSON file with input data defined. It will iterate over the items in the input JSON array and use `promptText` key of every item to ask it to the language model.

LLM answers are dumped in detail to a specified directory (one result per file) and the file is then linked in the aggregate output JSON.

At the moment, the script supports models from OpenAI and Google.

Supported OpenAI models:
* GPT-4o (`openai:gpt-4o`)
* GPT-4o-mini (`openai:gpt-4o-mini`)
* o3-mini (`openai:o3-mini`)

Supported Google models:
* Gemini 2.0 Flash (`gemini:2.0-flash`)
* Gemini 2.0 Flash Lite (`gemini:2.0-flash-lite`)
* Gemini 2.0 Flash Thinking Experimental (`gemini:2.0-flash-thinking-exp-01-21`)

Other models by these vendors are likely supported as well. In order for the script to allow querying them, insert relevant entry to `SUPPORTED_VARIANTS` list in respective file in the `clients/` directory.

## Configuration
The script accepts a set of parameters, that can be passed through the command-line invocation or using a JSON file. If a parameter is passed both ways, the value specified in command line takes precedence.

### Command-line invocation
Example command:
```
ask_llm.py input.json output.json --model openai:gpt-4o-mini --apiKey api-key-here
```

There are two obligatory parameters: path to the input file and path to the output file, that have to be passed in the command line. The input file contains all the prompts to use, while the output file will additionally store names of files with the LLM responses (see below for exact file schemas). Do not specify output as the same file as input: it will discard all entries that haven't been processed at the time the script terminates.

If the output file already exists and it's a JSON file, it *will not* be overwritten. Instead, new results will be appended to the existing ones. Additionally, unless told to start at 0 (`--skip 0`), the script will attempt to continue its work, meaning it will skip as many entries as there are already in the output file.

The execution continues as long as there are entries to process (either until the end of file or until `--limit` is reached), but you can abort processing any time by clicking `Ctrl+C`. All the progress will be then saved to the output file. Note: the dumps are saved right after receiving response from the LLM, but the main output file is written only once, at the end of script (either forced or normal).

The script accepts a set of additional parameters, most of them optional:
* `--model` (or `-m`) – designation of the model to be used (run `ask_llm.py -h` to see list of supported models). Mandatory.
* `--apiKey` (or `-a`) – the API key to use to authenticate yourself; obtain this from the model provider's website. Mandatory.
* `--dumps` – directory where to store the dumps of model responses, by default `dumps/` subdirectory in the current directory.
* `--skip` (or `-s`) – how many initial entries to skip in the input file, by default the number of entries that exist in the output file or 0 if the output does not exist.
* `--limit` (or `-l`) – how many queries to perform, by default there's no limit (all entries from the input files, except the skipped ones).
* `--delay` (or `-d`) – how many seconds to wait between subsequent requests to the model, by default 4 seconds.
* `--config` (or `-c`) – path to a JSON file from which to load additional parameters, unspecified in the command-line invocation.
* `--dryRun` – if set, the requests will not be sent to the LLMs, but all remaining processing is done as usual (note, that it does not bring the delay to zero, set `-d 0` not to wait between the requests).
* `--print` – if set, the prompts will be printed to the console.

### JSON config files
Part of the configuration can be specified in JSON files. You can use the `--config` (or `-c`) option to load a config file. Such file is an object, where keys are the param names (long versions, without `--` in the beginning), e.g.:
```json
{
    "model": "gemini:2.0-flash-lite",
    "delay": 5,
    "limit": 100,
    "dryRun": true
}
```

In this example, `model`, `delay`, `limit`, and `dryRun` will be applied, unless other values for them are specified in the command line. Additionally, it's possible to extend configuration files, using `$extends` key, like in the following:
```json
{
    "$extends": "example-base.json",
    "limit": 1
}
```

When combined with the above, it will have an effect of setting `limit` to 1 and all other fields as in the former config. A config file can extend only a single other file (so there's no multiple inheritance), but there is no limit on the depth of the hierarchy (a file can both extend another and be extended by yet another). Cycles in the inheritance chain are detected and will result in an error.

The configuration files are especially useful for storing API keys and options that change rarely.

## Input schema
The script expects that you have a JSON file, being an array of objects looking like that:
```json
{
    "id": "some identifier",
    "data": {},
    "promptText": "Lorem ipsum"
}
```
The object consists of three fields, out of which only `promptText` is mandatory:
* `promptText` – the text that the script will ask to the LLM.
* `id` – if present, will be included in the console output and in the names of LLM response dumps. Setting this field may help in debugging, but it's not mandatory. If not specified, identifiers like entry_00001 will be used.
* `data` – optional data that will be passed to the output file. Contents of this object is not processed and may be anything.

An example input file can be seen in [data/example.json](data/example.json).

## Output schema
The output file will have a very similar structure to the input file. It is an array of objects like that:
```json
{
    "id": "some identifier",
    "data": {},
    "promptText": "Lorem ipsum",
    "result": {
        "success": true,
        "dump": "full-path/to/llm-optional id-2025-04-09T18.40.36.json"
    }
}
```
Fields `id`, `data`, and `promptText` have the same meaning as in the input files. `data` will be present or not, depending whether it was set in the input. `id` and `promptText` will be always included.

The additional field, `result`, describes the output. It will always contain a `success` attribute, telling whether the prompt execution was successful. If so, field `dump` will be present. It points to a file that contains the LLM request and response (in particular, the text of both prompt and answer).

The separation between "general output file" and particular dumps is to make the main JSON file smaller and easier to process, especially for larger batches. The dump files will always have entry id in their names (or first 80 characters if the id is too long), so as to make it easy to match dumps to their descriptions.

## Magic words
If you need to include a dynamic part in your prompts, you can use so-called "magic words". Their syntax is like `{{#magicword:param}}` and they can be defined in [magic_words.py](utils/magic_words.py) file. This file contains a description of how the magic words can be used and defined.

As an example, an "include" magic word is specified there, which includes contents of a specified file into the prompt, where the magic word exists, eg. `{{#include:path/to/file.txt}}`.
