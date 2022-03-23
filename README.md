<h1 align="center">Zero Bot</h1>

<h3 align="center">
A private bot for my friend's discord server.
</h3>

## Commands

Currently it has 4 commands.

- `Poll`
- `Websearch`
- `Serversearch`
    - Scrapes [disboard](https://disboard.org) and displays each search result as an embed. I copy pasted my [paginator](ext/paginator.py) from one my other projects and modified it according to my needs.
- `Verification`
    - `set`
        - Sets the verification channel. Must be used before creating the role.
    - `create_role`
        - Creates a role whose members are unable to see any other channel except the channel that was set using the `set` subcommand.
    - `update_message`
        - Create the verification message or update the content of it if it already exists.
- `Publicremind`
    - Let everyone get reminded for some event.

    - `new`
        - Set a new reminder.
    - `set_backup_channel`
        - If the user's DMs are off, the bot will remind them in this channel instead.