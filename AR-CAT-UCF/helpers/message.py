from bot import client
import discord
import aiohttp
from logging.syslogger import log
import asyncio

async def post_message(channel, content) -> bool:
    timebuffer = 7
    max_attempts = 4
    
    for attempt_num in range(1, max_attempts + 1):
        try:
            if isinstance(content, str):
                await channel.send(content=content)
            elif isinstance(content, discord.Embed):
                await channel.send(embed=content)
            else:
                log.error(f"Invalid type!")
                return False
            
            log.info(f"Successfully sent message on {attempt_num} attempt.")
            return True
        except aiohttp.ClientConnectionError: # Client connection error
            log.error(f"⚠️ Connection error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
        except aiohttp.ClientError as e: # Client error
            log.error(f"⚠️ Client error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
        except Exception as e: # Other exceptions
            log.error(f"⚠️ Unexpected error occurred: {e} ... (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
            
        if attempt_num < max_attempts: # If we have attempts left
            await asyncio.sleep(timebuffer * attempt_num) # Sleep, again, multiplies. 
            
    log.warn(f"Failure to send message after {max_attempts} successive attempts!")
    
async def post_embed_with_image(channel, content, buf=None, fileName=None, url=None) -> bool:
    timebuffer = 7
    max_attempts = 4
    
    for attempt_num in range(1, max_attempts + 1):
        try:
            if buf and not url:
                buf.seek(0)
                file = discord.File(fp=buf, filename=fileName)
                await channel.send(embed=content, file=file)
            elif url and not buf:
                content.set_image(url=url)
                await channel.send(embed=content)
            
            log.info(f"Successfully sent message on {attempt_num} attempt.")
            return True
        except aiohttp.ClientConnectionError: # Client connection error
            log.error(f"⚠️ Connection error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
        except aiohttp.ClientError as e: # Client error
            log.error(f"⚠️ Client error (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
        except Exception as e: # Other exceptions
            log.error(f"⚠️ Unexpected error occurred: {e} ... (attempt {attempt_num}/{max_attempts}): Retrying in {timebuffer * attempt_num} seconds...")
            
        if attempt_num < max_attempts: # If we have attempts left
            await asyncio.sleep(timebuffer * attempt_num) # Sleep, again, multiplies. 
            
    log.warn(f"Failure to send message after {max_attempts} successive attempts!")
    return False