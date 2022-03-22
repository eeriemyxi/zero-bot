from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import disnake
from aiogtts import aiogTTS
from disnake.ext import commands

if TYPE_CHECKING:
    from bot import ZeroBot


class Voice(commands.Cog):
    def __init__(self, bot: ZeroBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: disnake.Member, _, after: disnake.VoiceState
    ):
        if not after.channel or member.bot:
            return None

        if hasattr(self, "voice_client"):
            while self.voice_client.is_playing():
                await asyncio.sleep(0.5)

        filename = f"vc_join_message_{member.id}.mp3"
        voice_channel = after.channel

        if voice_channel is not None:
            self.voice_client = await voice_channel.connect()
            await self.save_tts(
                f"{member.name} has joined the voice channel.", filename
            )

            source = disnake.FFmpegPCMAudio(filename)
            self.voice_client.play(source)

            while self.voice_client.is_playing():
                await asyncio.sleep(0.5)

            await self.voice_client.disconnect()
            del self.voice_client
            await self.bot.loop.run_in_executor(None, os.remove, filename)

    async def save_tts(self, text: str, filename: str):
        speech = aiogTTS()
        await speech.save(text, filename)
