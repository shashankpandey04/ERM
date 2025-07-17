import datetime
import re
import time
import discord
import pytz
from decouple import config
from discord.ext import tasks
import logging
import asyncio
import roblox
from collections import defaultdict

from utils.constants import RED_COLOR, BLANK_COLOR
from utils.prc_api import Player
from utils import prc_api
from utils.utils import run_command

@tasks.loop(minutes=1)
async def mc_discord_checks():
    """
    Automated Discord Checks for Maple County Servers.
    """