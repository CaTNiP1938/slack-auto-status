# Slack auto status
Linux bash tool to integrate with Slack and various calendar apps to auto set a status for your Slack profile across all the configured workspaces

## Requirements

The following `bash` libraries are needed (apart from the default ones) to run the script:

* JQ (https://jqlang.github.io/jq/)

## Configuration

The configuration is managed by a JSON file, named `config.json`. The list of the configuration options and their meaning is listed below:

**Debug mode:**
* Name: `debug`
* Type: `boolean`
* Value: Changes some logging and error handling behaviour. Set to `true` only if you are developing the script.

<br>

**Silent output:**
* Name: `silentOutput`
* Type: `boolean`
* Value: If set, the outputs of the commands are silenced, and only custom logs are displayed.

<br>

**Slack API tokens:**
* Name: `slackApiTokens`
* Type: `arr[string]`
* Value: Add a list of Slack app bearer tokens, and the status will be set to each of the workspaces associated with them.

<br>

**Status emoji:**
* Name: `statusEmoji`
* Type: `arr[string]`
* Value: The code of the Slack emoji used for the status setting. This emoji will be present next to your name.


## Install

After the repository is cloned to a system with `bash` installed and the configuration is set, all you need to do is to set the privileges of the script:

```sh
sudo chmod 777 ./script.sh
```

## Usage

To use the script, simply run it: 

```sh
./script.sh
```

You can integrate/automate the script running with other tasks.