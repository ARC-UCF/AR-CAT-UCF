from classes import Schedule, Message
from databases import write_messages, fetch_messages
from helpers import post_message, channels
from logger import log
from datetime import datetime, timedelta
import asyncio
import discord
from config import config

class Messenger():
    def __init__(self):
        self.preset_messages = [
            Message.new(
                id="hurr_1_month",
                header="Hurricane Season Starts Soon: Are You Prepared?",
                message=f"The Atlantic Hurricane Season starts June 1st and ends November 31st. Now is the time to prepare for hurricane season!\n\nReview your plans for when a hurricane threatens the area, and check your FEMA flood zone. Consider stocking up on water, non-perishables, and batteries in advance of any storms. Have multiple ways to receive weather alerts from the NWS, including any radio which can listen to NOAA Weather Radio, or by listening to any local news station, or by having a weather app, a cellular device, or receiving alerts by word of mouth.\n\nConsider what you need to protect your home and property from wind and water damage. If you are in a flood-prone area, consider getting sandbags, flood barriers, or have other means of protecting your home from flooding.\n\nAtlantic Tropical Cyclone Genesis Outlooks will begin again on June 1st, {datetime.now().year}\n\n**Below are a few resources which may be helpful for this upcoming Atlantic Hurricane Season:**\n[UCF Hurricane Information](https://www.ucf.edu/hurricane/)\n[National Hurricane Center: Hurricane Preparedness](https://www.noaa.gov/hurricane-prep)\n[Graphical Tropical Weather Outlooks](http://www.nhc.noaa.gov/gtwo_atl.shtml)\n[CECS Wiki Hurricane Links and Info](https://newton.i2lab.ucf.edu/wiki/Hurricanes)",
                footer="This message is sent automatically on the first of May",
                channel="hurricane",
                schedule=Schedule(
                    months=5,
                    days=1,
                    hours=12,
                    minutes=0,
                    grace_period=timedelta(minutes=30)
                )
            ),
            Message.new(
                id="hurr_day_before",
                header=f"The {datetime.now().year} Atlantic Hurricane Season Starts Tomorrow",
                message=f"The Atlantic Hurricane Season starts tomorrow, June 1st, and ends November 31st.\n\nAR-CAT-UCF will begin posting Atlantic Tropical Cyclone Genesis Outlooks tomorrow.\n\nAs a reminder, consider taking small steps to prepare for hurricane season! Consider stocking up on or checking your stock of batteries, consider purchasing a radio capable of receiving NOAA weather alerts, ensure you have non-perishable food, and have multiple ways to receive weather alerts from local government agencies, which includes via NOAA weather radio, cellular device, weather app, sirens, news station, or by word of mouth.\n\nFEMA recommends stocking up on three days worth of supplies per person in the case of any natural disaster.\n\nCheck your Flood Zone by checking [FEMA's Flood Zone Map](https://msc.fema.gov/portal/search).\n\n**Other links which might be helpful:**\n[UCF Hurricane Information](https://www.ucf.edu/hurricane/)\n[National Hurricane Center: Hurricane Preparedness](https://www.noaa.gov/hurricane-prep)\n[CECS Wiki Hurricane Links and Info](https://newton.i2lab.ucf.edu/wiki/Hurricanes)\n\nRemember: **don't be scared, be prepared!**",
                footer="This message is sent automatically on the 31st of May",
                channel="hurricane",
                schedule=Schedule(
                    months=5,
                    days=31,
                    hours=12,
                    minutes=0,
                    grace_period=timedelta(minutes=30)
                )
            ),
            Message.new(
                id="hurr_peak_months",
                header=f"The Peak of the {datetime.now().year} Atlantic Hurricane Season Is Soon",
                message=f"The historical peak of the hurricane season is soon, and spans from mid-August to mid-October, from approximately August 15th to October 15th. The historical peak is September 15th.\n\nAR-CAT will continue to post daily Atlantic Tropical Cyclone Genesis outlooks until December 1st.\n\nAs a reminder, you can check your FEMA flood zone by visiting [FEMA's Flood Zone Map](https://msc.fema.gov/portal/search).\n\n**You may find these other links to be helpful:**\n[UCF Hurricane Information](https://www.ucf.edu/hurricane/)\n[National Hurricane Center: Hurricane Preparedness](https://www.noaa.gov/hurricane-prep)\n[CECS Wiki Hurricane Links and Info](https://newton.i2lab.ucf.edu/wiki/Hurricanes)\n\nMake sure you're prepared for this hurricane season!",
                footer="This message is sent automatically on the 31st of July",
                channel="hurricane",
                schedule=Schedule(
                    months=7,
                    days=31,
                    hours=12,
                    minutes=0,
                    grace_period=timedelta(minutes=30)
                )
            ),
            Message.new(
                id="hurr_month_end",
                header=f"The {datetime.now().year} Hurricane Season Has Ended",
                message=f"The {datetime.now().year} hurricane season has ended. Hurricane seasons ends today, December 1st. Hurricanes or tropical storms may still occur in the off-season, but the likelihood is very limited, given poor conditions for their development. The {datetime.now().year + 1} hurricane season will begin June 1st.",
                footer="This message is sent automatically on the 1st of December",
                channel="hurricane",
                schedule=Schedule(
                    months=12,
                    days=1,
                    hours=12,
                    minutes=0,
                    grace_period=timedelta(minutes=30)
                )
            ),
            Message.new(
                id="florida_wet_season_begin",
                header=f"Florida's Rainy Season Begins Soon",
                message=f"Florida's historical rainy season begins soon. Florida's rainy season historically begins around May, but will peak come August to October. Thunderstorms will gradually become a daily occurrence during this period.\n\nBring an umbrella or other rain gear with you! Plan your days with thunderstorms and rain showers in mind, and be prepared to move indoors should thunder roar. If you can hear thunder, you are close enough to be struck by lightning!\n\nThe morning to late evening hours will provide the best times to be outdoors - minimal heat plus lack of thunderstorm activity will allow ample time to setup radio stations and take them down before the arrival of lightning and/or rain. Some storms can become strong to severe on any given day during this period due to the sea breeze.",
                footer="This message is sent automatically on the 10th of May",
                channel="forecast",
                schedule=Schedule(
                    months=5,
                    days=10,
                    hours=11,
                    minutes=0,
                    grace_period=timedelta(minutes=30)
                )
            )
        ]
        self.messages_cache: dict[str, Message] = {}
        
        self._read_messages()
        
        log.info(f"Messages ready.")
        
    def _read_messages(self):
        msgs = fetch_messages()
        
        if msgs:
            for key, msg in msgs.items():
                Msg: Message = Message.from_dict(data=msg)
                
                self.messages_cache[Msg.id] = Msg
                
                log.info(f"Read messages")
        else:
            log.info(f"No messages to read were found; skipping this step.")
            
        for msg in self.preset_messages:
            if msg.id in self.messages_cache:
                curr_msg = self.messages_cache[msg.id]
                
                if curr_msg.id == msg.id:
                    if curr_msg.schedule != msg.schedule:
                        log.info(f"Overwriting message in message cache, updating schedule.")
                        self.messages_cache[msg.id] = msg
            else:
                self.messages_cache[msg.id] = msg
    
    async def check_and_post(self):
        for key, msg in self.messages_cache.items():
            if msg.schedule.should_send(msg.last_sent, datetime.now()):
                embed = discord.Embed(
                    title=msg.header,
                    description=msg.message,
                    color=0x1e90ff,
                )
                
                embed.set_footer(text=f"{config.version_id} | {msg.footer}")
                
                send_channel = channels.get_channel_from_name(msg.channel)
                
                success = await post_message(channel=send_channel, content=embed)
                
                if success:
                    msg.last_sent = datetime.now()
                else:
                    log.error(f"Failed to send message {key}")
                    
        messages_to_write = {}
        
        for key, msg in self.messages_cache.items():
            messages_to_write[key] = msg.to_dict()
            
        write_messages(messages_to_write)
        
        await asyncio.sleep(60)