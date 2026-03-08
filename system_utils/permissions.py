import discord
from discord import app_commands
from rank_config import permissions

def get_rank(member: discord.Member):
    if not isinstance(member, discord.Member):
        print("User is not in the server.")
        return 0
    
    roles_to_check = [r for r in member.roles if r.id in permissions.keys()]
    
    if not roles_to_check:
        return 0
    
    highest_rank = 0
    
    for r in roles_to_check:
        if r.id in permissions.keys():
            rank = permissions.get(r.id, 0)
            
            if rank > highest_rank: highest_rank = rank
            
    print(f"Users rank is {highest_rank}")
    return highest_rank

class RankError(app_commands.AppCommandError):
    pass

def requires_minimum_rank(min_rank: int):
    async def predicate(interaction: discord.Interaction) -> bool:
        user = interaction.user
        rank = get_rank(user)
        
        if rank < min_rank:
            raise RankError(f"This command requires a permissions rank of {min_rank}, but the user running the command has a rank of {rank}.")
        return True
    return app_commands.check(predicate)