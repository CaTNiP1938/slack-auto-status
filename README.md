# Slack auto status
Python tool to integrate with Slack and various calendar apps to auto set a status for your Slack profile across all the configured workspaces

## Requirements

The python version used is `Python 3.10.12` but other Python3 versions will probably work as well.

## Configuration

The configuration is managed by a JSON file, named `config.json`. The list of the configuration options and their meaning is listed below:

<br>

**Silent output:**
* Name: `silentOutput`
* Type: `boolean`
* Required: `false`, default is `true`
* Value: If set, the outputs of the commands are silenced, and only custom logs are displayed.

<br>

**Slack API tokens:**
* Name: `slackApiTokens`
* Type: `arr[string]`,
* Required: `true`
* Value: Add a list of Slack app bearer tokens, and the status will be set to each of the workspaces associated with them.

<br>

**Slack User Ids:**
* Name: `slackUserIds`
* Type: `arr[string]`,
* Required: `true`
* Value: For each token, add the corresponding user's id you want to set the status to.

<br>

**Status emoji:**
* Name: `statusEmoji`
* Type: `string`
* Required: `false`, default is `:speech_balloon:`
* Value: The code of the Slack emoji used for the status setting. This emoji will be present next to your name.

<br>

**Meeting status emoji:**
* Name: `meeintStatusEmoji`
* Type: `string`
* Required: `false`, default is `:calendar:`
* Value: The code of the Slack emoji used for the annotation of meetings.



## Install

After the repository is cloned to a system with python3 installed and the configuration is set, all you need to do is to set the privileges of the script:

```sh
sudo chmod 777 ./script.py
```

## Usage

To use the script, simply run it: 

```sh
python3 ./script.py
```

You can integrate/automate the script running with other tasks.

## Linting

There is a `.flake8` configuration file for the linting of the python code.

## Slack configuration

...
- Slack desktopon - nev: tools & settings, workspace settings
- Weboldalon oldalt configure apps, job felül build
- Create new app from scratch
    - App name: SlackStatusToken
    - Workspace legyen a workspace és create
- Bal oldalt OAuth & Permissions, User Token Scopes-nál Add an OAuth scope, users.profile:write
- Kicsit följebb, Install to Workspace > allow, xoxp-al kezdődő tokent kimásolni