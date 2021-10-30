"""
This is just that part that deals with very basic search queries to mongodb.
The reason behind including these functions is that they were used multiple
times in the code.
"""

from loader import teams, users, queues


async def get_team_id(user_id):
    """
    Returns the team id of a user based on his/her user id.
    (this is just a very simple query to mongodb)
    """
    data = await users.find_one(
        {"user_id": user_id},
        {"team_id": 1, "_id": 0},
    )
    team_id = data["team_id"]

    return team_id


async def get_team_members(team_id):
    """
    Return the team members a user has based on his/her team id.
    (this is also another very simple query to mongodb)
    """
    team_data = await teams.find_one(
        {"id": team_id},
        {"members": 1, "_id": 0},
    )
    members = team_data["members"]

    return members


async def get_queue_array(team_id, queue_type):
    """
    Returns the queue array for a particular queue type for a specific team id.
    (yet again a very simple search query)
    """
    queues_data = await queues.find_one(
        {"id": team_id},
        {"queues": 1, "_id": 0},
    )
    queue_array = queues_data["queues"][queue_type]

    return queue_array


async def get_queue_list(queue_array):
    """
    Returns the queue list using the queue array.
    (this function will mainly be called by another function)
    """
    queue_list = ""
    for index, member in enumerate(queue_array, start=1):
        name = member["name"]
        queue_list += f"{index}. {name}\n"

    return queue_list

async def get_setup_person(team_id):
    """
    Returns the name of the person who is doing all the setup in a given team.
    """
    setup_person = await users.find_one(
        {"user_id": int(team_id)},
        {"name": 1, "_id": 0},
    )

    return  setup_person["name"]

