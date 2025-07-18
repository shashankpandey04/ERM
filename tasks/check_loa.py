import datetime

import discord
from decouple import config
from discord.ext import commands, tasks

from utils.constants import RED_COLOR, BLANK_COLOR


@tasks.loop(minutes=1, reconnect=True)
async def check_loa(bot):
    try:
        loas = bot.loas

        async for loaObject in bot.loas.db.find():
            if (
                datetime.datetime.now().timestamp() > loaObject["expiry"]
                and loaObject["expired"] is False
            ):
                if loaObject["accepted"] is True:
                    loaObject["expired"] = True
                    await bot.loas.update_by_id(loaObject)
                    guild = bot.get_guild(loaObject["guild_id"])
                    if guild:

                        member = guild.get_member(loaObject["user_id"])
                        settings = await bot.settings.find_by_id(guild.id)
                        roles = [None]
                        role_removed = None
                        if settings is not None:
                            if "loa_role" in settings["staff_management"]:
                                try:
                                    if isinstance(
                                        settings["staff_management"]["loa_role"], int
                                    ):
                                        roles = [
                                            discord.utils.get(
                                                guild.roles,
                                                id=settings["staff_management"][
                                                    "loa_role"
                                                ],
                                            )
                                        ]
                                    elif isinstance(
                                        settings["staff_management"]["loa_role"], list
                                    ):
                                        roles = [
                                            discord.utils.get(guild.roles, id=role)
                                            for role in settings["staff_management"][
                                                "loa_role"
                                            ]
                                        ]
                                except KeyError:
                                    pass

                        docs = bot.loas.db.find(
                            {
                                "user_id": loaObject["user_id"],
                                "guild_id": loaObject["guild_id"],
                                "accepted": True,
                                "expired": False,
                                "denied": False,
                                "type": loaObject["type"],
                            }
                        )
                        should_remove_roles = True
                        async for doc in docs:
                            if not doc == loaObject:
                                should_remove_roles = False
                                break

                        if should_remove_roles:
                            for role in roles:
                                if role is not None:
                                    if member:
                                        if role in member.roles:
                                            try:
                                                await member.remove_roles(
                                                    role,
                                                    reason="LOA Expired",
                                                    atomic=True,
                                                )
                                            except discord.HTTPException:
                                                role_removed = "**Alert:** ⚠️ Failed to remove LOA role due to discord issues.\nContact your Management to manually remove the role!"
                                                pass
                        if member:
                            try:
                                await member.send(
                                    embed=discord.Embed(
                                        title=f"{loaObject['type']} Expired",
                                        description=f"Your {loaObject['type']} has expired in **{guild.name}**\n{role_removed if role_removed != None else ""}.",
                                        color=BLANK_COLOR,
                                    )
                                )
                            except discord.Forbidden:
                                pass
    except ValueError:
        pass
