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
        self.postponed = set()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member: disnake.Member, _, after: disnake.VoiceState
    ):
        if not after.channel or member.bot:
            return None

        if hasattr(self, "voice_client"):
            if self.voice_client.is_connected():
                self.postponed.add(member)
                return None

            while self.voice_client.is_connected():
                asyncio.sleep(0.3)

        voice_channel = after.channel

        if voice_channel is not None:
            self.voice_client = await voice_channel.connect()
            await self.play(member, voice_channel)

            for memb in self.postponed:
                print(memb)
                await self.play(memb, voice_channel)

            self.postponed.clear()

            await self.voice_client.disconnect()

    async def save_tts(self, text: str, filename: str):
        speech = aiogTTS()
        await speech.save(text, filename)

    async def play(self, member: disnake.Member, channel: disnake.VoiceChannel):
        if (
            member.voice
            and member.voice.channel
            and member.voice.channel is not channel
        ):
            await self.voice_client.disconnect()
            self.voice_client = await member.voice.channel.connect()

        filename = f"vc_join_message_{member.id}.mp3"
        await self.save_tts(f"{member.name} has joined the voice channel.", filename)
        source = disnake.FFmpegPCMAudio(filename)

        self.voice_client.play(source)
        while self.voice_client.is_playing():
            await asyncio.sleep(0.5)

        await self.bot.loop.run_in_executor(None, os.remove, filename)
