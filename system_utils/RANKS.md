# Rank Overview

Listed below are the three ranks (0 to 2) which are part of the system for the bot. Read below each of the permissions granted to each rank to determine what is suitable for each role you think needs to have access to the bot. Currently, these are the only ranks available. More ranks may be added in the future as determined necessary.

## Admin Permissions (Rank 2)

Admin permissions are separate from user permissions and all permissions, as Admins will have more access to system features meant for management and organization. Such features and commands includes:

* Enable/disable repeater voice
* Create special weather/alert "announcements" and post them to a corresponding channel, including announcement channels
* Create voice snippets from the (future) custom TTS
* Assign/remove other users and roles from being able to use admin or user permissions
* Assign new colors to alert colors
* Change the Interruption Aggressiveness for the system
* Change individual Interruption Aggressiveness numbers for specific alerts
* Dynamically changing the cycle time of the bot
* Other administrative/miscelleanous commands and features

These permissions will otherwise include commands which are meant to be administrative and related to configuration of the bot, as will be added over time. Correspondingly, this document will be updated when needed to detail the difference between Admin and User capabilities.

## User Permissions (Rank 1)

User permissions allow users to work with the bot to do other miscelleanous tasks, and not execute on admin commands. This includes:

* Sending safety-related messages when needed
* Other basic features which are non-administrative

## All User Permissions (Rank 0)

Rank 0 permissions include any other interactability with the bot where it does not include the sending of messages or other features which could interfere with the server, which includes:

* Viewing the update log, creating bug reports, or asking for features, and being linked to the corresponding space to make those requests (which is here)
* Viewing current severe weather outlooks
* Viewing graphical hazardous outlooks from any one of the three NWS offices (in the future)
* Viewing active alerts
* Other interactions intended to be accessed through the bot

# Assigning Ranks

Rank should be assigned based on need and access to features.

For example, a user should be granted User permissions if you want them to be able to send safety messages as needed but do not want them to have access to more administrative features. Or, if you want someone to be able to manage the bot and its features, grant them Admin permissions. 

**Be aware that Admins will not be able to revoke access from each other.** (A change for a Owner role or something similar might be considered to allow for management of admin users.)

If the corresponding database holding the granted permissions is deleted, it will revert to the default configuration for the bot. 