# methods/GuildProfileUpdater.py
from discord.http import Route
"""
GuildProfileUpdater
--------------

Wrapper around Discord's HTTP API for modifying the bot's own
guild member profile. This enables early adoption of unreleased
discord.py features such as setting guild-specific bio, banner,
and avatar.

Usage:
    from utils.methods import GuildProfileUpdater

    profile_updater = GuildProfileUpdater(bot)
    await profile_updater.set_profile(
        guild_id=123456789012345678,
        nick="YourBotNick",
        bio="This is my guild bio!",
        banner=discord.File("banner.png"),   # It will be converted to base64
        avatar=discord.File("avatar.png")    # It will be converted to base64
    )
"""

import base64
import mimetypes
from typing import Optional, Dict, Any, Union

import discord


class GuildProfileUpdater:
    """
    Provides methods to modify the bot's own guild member profile.
    """

    def __init__(self, bot):
        """
        Parameters
        ----------
        bot : discord.Client | commands.Bot
            The running bot instance from discord.py
        """
        self.bot = bot

    async def file_to_data_uri(self, file: Union[discord.File, discord.Attachment]) -> str:
        """
        Convert a Discord file/attachment into a base64 data URI.

        Parameters
        ----------
        file : discord.File | discord.Attachment
            The file or attachment to convert.

        Returns
        -------
        str
            A base64 data URI string.
        """
        if isinstance(file, discord.Attachment):
            data = await file.read()
            mime = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        elif isinstance(file, discord.File):
            fp = file.fp
            if fp.seekable():
                fp.seek(0)
            data = fp.read()
            mime = mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
        else:
            raise TypeError("Expected discord.File or discord.Attachment")

        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    async def set_profile(
        self,
        guild_id: int,
        *,
        nick: Optional[str] = None,
        bio: Optional[str] = None,
        banner: Optional[Union[str, discord.File, discord.Attachment]] = None,
        avatar: Optional[Union[str, discord.File, discord.Attachment]] = None
    ) -> Dict[str, Any]:
        """
        Modify the bot's guild-specific profile.

        Parameters
        ----------
        guild_id : int
            The guild ID to modify the profile in.
        nick : str, optional
            Nickname for the bot in the guild (requires CHANGE_NICKNAME).
        bio : str, optional
            Guild member bio text.
        banner : str | discord.File | discord.Attachment, optional
            Base64-encoded data URI or file/attachment for the banner image.
        avatar : str | discord.File | discord.Attachment, optional
            Base64-encoded data URI or file/attachment for the avatar image.

        Returns
        -------
        dict
            The updated member object from Discord API.

        Raises
        ------
        ValueError
            If no fields are provided to update.
        HTTPException
            If the Discord API request fails.
        """
        fields: Dict[str, Any] = {
            "nick": nick,
            "bio": bio,
        }

        if banner is not None:
            if isinstance(banner, (discord.File, discord.Attachment)):
                fields["banner"] = await self.file_to_data_uri(banner)
            else:
                fields["banner"] = banner

        if avatar is not None:
            if isinstance(avatar, (discord.File, discord.Attachment)):
                fields["avatar"] = await self.file_to_data_uri(avatar)
            else:
                fields["avatar"] = avatar

        payload = {k: v for k, v in fields.items() if v is not None}

        if not payload:
            raise ValueError("No fields provided to update.")

        route = Route(
            "PATCH",
            "/guilds/{guild_id}/members/@me",
            guild_id=guild_id
        )
        return await self.bot.http.request(route, json=payload)