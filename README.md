# Slack auto status
Python tool to integrate with Slack and various calendar apps to auto set a status for your Slack profile across all the configured workspaces.

## Requirements

The python version used is `Python 3.10.12` but other Python3 versions will probably work as well. You also need to have the associated `pip3` package manager installed.

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

<br>

**Timezone to use:**
* Name: `localTimeZone`
* Type: `string`
* Required: `true`
* Value: The timezone to convert meetings to in case an integration sends meetings date in UTC. Example value: `Europe/Amsterdam`

<br>

**Integrations:**
* Name: `integrations`
* Type: `dict[<integration_name>, <integration_dict>]`
* Required: `true`
* Value: This contains all integrations and the credentials associated with them if needed:

<br>

* ***<integration_dict>***
    * Name: **Name of the integration** (f.e. google_calendar)
    * Type: `dict[<key_name>, <key_value>]`
    * Required: `true`
    * Value: Contains two key-value pairs related to that specific integration:
        * **Is enabled:**
            * Name: `is_enabled`
            * Type: `boolean`
            * Required: `true`
            * Value: If `true`, the integration will be used when requesting meeting from integrations.
        * **Credentials:**
            * Name: `credentials`
            * Type: `dict`
            * Required: `false`
            * Value: The respective integration's credentials are stored here, if they are needed.

## Install

After the repository is cloned to a system with python3 installed and the configuration is set, you need to adjustthe privileges of the script:

```sh
sudo chmod 777 ./script.py
```

Last thing is to install the required packages found in `requirements.txt`. To do this, run the following script:

```sh
pip3 install -r requirements.txt
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

## Google Calendar integration

To integrate with google calendar API, and get the calendar events, you need to set up an API on google side, then set the configuration in the config.json. Follow these steps:

1. On the [**Google Cloud**](https://console.cloud.google.com/projectselector2/apis/enableflow?apiid=calendar-json.googleapis.com&supportedpurview=project) platform, create a new project, or select an already existing one. 
2. After that, enable the Google Calendar API for the project with this [link].(https://console.cloud.google.com/flows/enableapi?apiid=calendar-json.googleapis.com)
3. Next, go to [**OAuth consent screen**](https://console.cloud.google.com/apis/credentials/consent) and select **External** as user type and click **Create**. Fill the required fields of the form: add an **App name**, and for **User support email** and **Developer contact information email**, you can add your own email address. Click **Save and continue**.
4. Next, go to the [**Credentials**](https://console.cloud.google.com/apis/credentials) page and follow these steps:
    - Click Create Credentials > OAuth client ID.
    - Click Application type > Desktop app.
    - In the Name field, type a name for the credential. This name is only shown in the Google Cloud console.
    - Click Create. The OAuth client created screen appears, showing your new Client ID and Client secret.
    - Click OK. The newly created credential appears under OAuth 2.0 Client IDs.
    - Save the downloaded JSON file temporarily as credentials.json.
    - Copy the contents into the `config.json` file, for the **integrations** > **google-calendar** > **credentials** key's value.
    - You also need to set the `enabled` field for the google-calendar integration in the config.
5. If you enable the google calendar integration, every time the meetings are chosen to be loaded from there, a browser tab will open to authenticate the user.


## Azure Teams integration

To integrate with azure teams API, and get calendar events, you need to set up an App registration on Microsoft Entra ID, then set the configuration in the config.json. Follow these steps:

1. Open the [**Microsoft Azure Portal**](https://portal.azure.com/#home). You may need to register with your Microsoft account, but you can choose **Free Tier**. Even if we use some credits (from the free tier) on creating the infrastructure, using it will not deplete it further, from my experience.
2. From **Azure services**, select [**Microsoft Entra ID**](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/Overview), and from the left side panel, choose [**App registrations**](https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps).
3. Hit **New registration**:
    - For the **Name**, you can choose anything, like ***Slack auto status***.
    - For the **Supported account types**, select ***Accounts in any organizational directory (Any Microsoft Entra ID tenant - Multitenant)***.
    - For the **Redirect URI**, select ***Public client/native (mobile & desktop)*** as a platform, and for the redirect URI, enter the following: ***http://localhost:8400***
4. Selecting the newly created App, navigate to the **Authentication** tab on the left menu. Scroll down and under **Advanced settings**, set **Allow public client flows** to **Yes**.
5. From the left side menu bar, now select **API permissions**. Configure the permissions so that two are present, both are **Microsoft Graph - Delegated permissions**:
    - Calendar.ReadBasic
    - User.Read
6. The app is now ready. Next, go to the **Overview** section of your app, and copy the client and tenant id into the `config.json` file, so the under **integrations** > **azure-teams** > **credentials**, the JSON structure looks like this:

```sh
    "client_id": <Application (client) ID - from overview>,
    "tenant_id": <Directory (tenant) ID -  from overview>,
```

7. Lastly, you will need to insert one more key into the credentials, your user's id inside teams. To get it, open your profile on teams, and the last button from the buttons under your name will be **three dots**, select it, then **Export data**. This will download a JSON file, and in that, under the **accounts** key, the first entry will have an **externalDirectoryObjectId** key. Copy that key's value (it will be a UUID) into the credentials file, like this:

```sh
    "user_id": <the user id you copied>
```

Also, don't forget to set the `enabled` field to `true` for the azure-teams integration in the config.

8. If you enable the azure teams integration, every time the meetings are chosen to be loaded from there, a browser tab will open to authenticate the user.

## Usage

To use the script, simply run it: 

```sh
python3 ./script.py
```

You can integrate/automate the script running with other tasks.

## Linting

There is a `.flake8` configuration file for the linting of the python code.
