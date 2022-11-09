import re
import subprocess

import discord
from redbot.core import commands


class Convert(commands.Cog):
    """Convert related commands."""

    def __init__(self):
        self.decimal = re.compile(r"\d+")

    @commands.command()
    async def convert(self, ctx, *, conversion: str):
        """Convert from different kinds of units to other units using pint
        Example:
        - `[p]convert <from> to <to>`
        - `[p]convert 23cm to in`
        - `[p]convert 5in + 5ft to cm`
        """

        if " to " not in conversion:
            await ctx.send(
                f"`{conversion}` is not a valid conversion. Please make sure it is in the format `[p]convert <from> to <to>`"
            )
            await ctx.send_help()
            return

        arg1, end_unit = conversion.split(" to ")

        amount = re.search(self.decimal, arg1).group()
        unit = arg1.replace(amount, "").strip()

        arg1 = f"{amount} {unit}"

        try:
            result = await ctx.bot.loop.run_in_executor(
                None, subprocess.check_output, ["units", arg1, end_unit]
            )
        except subprocess.CalledProcessError as e:
            error = e.output.decode("utf-8")
            # grab the first line for the error type
            error_type = error.splitlines()[0]
            embed = discord.Embed(
                title="Error",
                description=f"Error when converting `{conversion}`\n{error_type}",
                color=0xFF0000,
            )
        else:
            # the result is line 1
            result = result.decode("utf-8").splitlines()[0]
            # remove whitespace at the start and end
            result = result.strip()
            # check if first line has a * or /
            if "*" in result or "/" in result:
                # remove the first character
                result = result[1:]
            # create embed
            embed = discord.Embed(
                title="Convert",
                description=f"`{conversion}`\n`{result.strip()}{end_unit}`",
                color=0x00FF00,
            )

        await ctx.send(embed=embed)
