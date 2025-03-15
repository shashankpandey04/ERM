
import asyncio
from utils.prc_api import Player, ResponseFailure

'''
Condition Variables
- ERLC_Players
- ERLC_Moderators
- ERLC_Admins
- ERLC_Owner
- ERLC_Staff
- ERLC_Queue
- OnDuty
- OnBreak
- X_InGame
'''

'''
NOTABLE DESIGN LIMITATIONS
::: YOU MUST NOT HAVE SPACES IN YOUR CONSTANTS.
'''


def function_argument_count(func):
    return func.__code__.co_argcount


def argument_names(func):
    return func.__code__.co_varnames


'''
PREDETERMINED FUTURE FUNCTIONS
- These are asynchronous functions which help in the fetching of variables before passing to a custom function.
'''


async def get_queue(api_client, guild_id):
    return await api_client.get_server_queue(guild_id)


async def online_shifts(bot, guild_id):
    return [i async for i in bot.shift_management.shifts.db.find({"Guild": guild_id, "EndEpoch": 0})]


'''
CUSTOM FUNCTIONS
- The arguments you can provide in these functions are shown in the fetch_predetermined_futures function.
'''


def count_erlc_players(players: list[Player]):
    return len(players)


def count_erlc_moderators(players: list[Player]):
    return len(list(filter(lambda x: x.permission == "Server Moderator", players)))


def count_erlc_admins(players: list[Player]):
    return len(list(filter(lambda x: x.permission == "Server Administrator", players)))


def count_erlc_owners(players: list[Player]):
    return len(
        list(filter(lambda x: x.permission not in ["Server Moderator", "Normal", "Server Administrator"], players)))


def count_erlc_queue(queue: list[Player]):  # this one isnt supported for maple county yet
    return len(queue)


def x_ingame(players: list[Player], player: str):
    return player.lower() in [p.username.lower() for p in players]


def filter_online(shifts: list):
    return len(list(filter))


'''
Comparison Operators
(we're not stupid enough to use eval.)
'''


def equals_operator(v1: int, v2: int):
    return v1 == v2


def less_than_operator(v1: int, v2: int):
    return v1 < v2


def less_than_or_equals_to_operator(v1: int, v2: int):
    return v1 <= v2


def more_than_operator(v1: int, v2: int):
    return v1 > v2


def more_than_or_equals_to_operator(v1: int, v2: int):
    return v1 >= v2


def not_equals_to(v1: int, v2: int):
    return v1 != v2


operator_table = {
    "==": equals_operator,
    "<": less_than_operator,
    "<=": less_than_or_equals_to_operator,
    "!=": not_equals_to,
    ">": more_than_operator,
    ">=": more_than_or_equals_to_operator
}

variable_table = [
    "ERLC_Players",  # these obviously still work for maple county as well
    "ERLC_Moderators",
    "ERLC_Admins",
    "ERLC_Owner",
    "ERLC_Staff",
    "ERLC_Queue",  # this doesnt work for maple county :(
    "OnDuty",
    "OnBreak",
    "ERLC_X_InGame"
]

value_finder_table = {
    "ERLC_Players": count_erlc_players,
    "ERLC_Moderators": count_erlc_moderators,
    "ERLC_Admins": count_erlc_admins,
    "ERLC_Owners": count_erlc_owners,
    "ERLC_Queue": count_erlc_queue,
    "ERLC_X_InGame": x_ingame
}


def handle_comparison_operations(v1, v2, operator):
    function = operator_table[operator]
    return function(v1, v2)


def separate_arguments(condition):
    return condition.split(" ")[0], condition.split(" ")[1:]  # ERLC_XInGame i_iMikey


async def handle_value(value, futures) -> int:
    condition, args = separate_arguments(value)
    if condition not in variable_table:
        return value  # this means we're comparing a raw constant
    else:
        func, func_args = determine_func_info(condition)
        submitted_arguments = []
        for item in func_args:
            submitted_arguments.append(futures[item.lower()]())

        if len(func_args) > 1:
            return func(*submitted_arguments, *args)
        else:
            return func(*submitted_arguments)


def determine_func_info(cond):
    func = value_finder_table[cond]
    return func, argument_names(func)


async def fetch_predetermined_futures(bot, guild_id, condition, value, api_client=None):
    return {
        "queue": lambda: asyncio.run(get_queue(api_client, guild_id)),
        "shifts": lambda: asyncio.run(online_shifts(bot, guild_id)),
        "bot": lambda: bot,
        "guild_id": lambda: guild_id,
        "condition": lambda: condition,
    }
