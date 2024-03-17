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
* Value: For each token, add the corresponding user's id you want to set the status to. The order musst be the sameas for the tokens.

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

## Slack configuration

To integrate with slack, and to be able to set the status via an Slack API endpoint call, you will need an api token. A token can be granted only through a Slack app installed to the workspace. This can be a dedicated app, with the appripriate permissions granted, or ad-hoc app, created only for this purpose. The latter case is described here, but if you have a dedicated app, you can skip ahead and just copy the api key + the user id (6. and 7. steps).

Before you can ask the workspace administrator to create and install an app for you, you have to mention that you can alter any person's account info with the api token, since the permission to set the status is in one package with the permission of setting user info.

If they agree on this, or you are the administrator, to install a new app and get the token required, you have to do the following steps:

1. On the Slack Desktop application, in the upper left corner, click on the workspace name, on **Tools & Settings** then on **Workspace settings**.
2. After the webpage fully loads, cloick on **Configure apps** in the upper right corner.
3. Click **Create new app from scratch**. Add a name (f.e. SlackStatusToken), and for the workspace, select the one you are working with.
4. After the app is created, on the left side, select **OAuth & Permissions**, scroll down, and at **User Token Scopes**, select **Add an OAuth scope**, then from the list, you have to choose **users.profile:write**. This is the only permission required for our app.
5. Scroll back up, and click **Install to Workspace**. This will ask if you proceed o give the selected permissions, and if you select **Allow**, the app will be installed to the workspace.
6. The webpage you are routed to will show the new **xoxp** token. Copy it into the **config.json** file.
7. The last step is to copy the user id as well, this way you can set which user's status you'd like to adjust. This differs on every workspace. You can find it by clicking on he profile in Slack (or **View full profile**). If the tab on the right part of the window appears, Click the **three dots**, then **Copy member ID**. This goes to the user ID section of the config file.

## Usage

To use the script, simply run it: 

```sh
python3 ./script.py
```

You can integrate/automate the script running with other tasks.

## Linting

There is a `.flake8` configuration file for the linting of the python code.
