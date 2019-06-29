import asyncio
import logging
import datetime

import pymongo
import discord
from discord.ext import commands

import config

mclient = pymongo.MongoClient(
	config.mongoHost,
	username=config.mongoUser,
	password=config.mongoPass
)

serverLogs = None
modLogs = None

@commands.command()
async def warn(ctx, member: discord.Member, *args):
    if len(args) < 1:
        return await ctx.send(':warning: A reason is required')

    reason = ''
    for x in args:
        reason += f'{x} '        
    db = mclient.fil
    puns = db.puns
    users = db.users

    tier1 = ctx.guild.get_role(config.warnTier1)
    tier2 = ctx.guild.get_role(config.warnTier2)
    tier3 = ctx.guild.get_role(config.warnTier3)

    Roles = member.roles
    warnLevel = 0
    for role in Roles:
        if role == tier3:
            return await ctx.send(f':warning: {member.name}#{member.discriminator} is already at the highest warn tier!')
        
        elif role == tier2:
            warnLevel = 2
            Roles.remove(role)
            Roles.append(tier3)

            embed = discord.Embed(color=discord.Color(0xD0021B), timestamp=datetime.datetime.utcnow())
            embed.set_author(name=f'Third Warning | {member.name}#{member.discriminator}')
            embed.add_field(name='User', value=f'<@{member.id}>', inline=True)
            embed.add_field(name='Moderator', value=f'<@{ctx.author.id}>', inline=True)
            embed.add_field(name='Reason', value=reason)
        
        elif role == tier1:
            warnLevel = 1
            Roles.remove(role)
            Roles.append(tier2)
            
            embed = discord.Embed(color=discord.Color(0xFF9000), timestamp=datetime.datetime.utcnow())
            embed.set_author(name=f'Second Warning | {member.name}#{member.discriminator}')
            embed.add_field(name='User', value=f'<@{member.id}>', inline=True)
            embed.add_field(name='Moderator', value=f'<@{ctx.author.id}>', inline=True)
            embed.add_field(name='Reason', value=reason)
    
    if warnLevel == 0:
        Roles.append(tier1)

        embed = discord.Embed(color=discord.Color(0xFFFA1C), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f'First Warning | {member.name}#{member.discriminator}')
        embed.add_field(name='User', value=f'<@{member.id}>', inline=True)
        embed.add_field(name='Moderator', value=f'<@{ctx.author.id}>', inline=True)
        embed.add_field(name='Reason', value=reason[:-1])
    
    await member.edit(roles=Roles, reason='Warning action by Moderator')
    await modLogs.send(embed=embed)

    return await ctx.send(f':heavy_check_mark: Issued a Tier {warnLevel + 1} warning to {member.name}#{member.discriminator}')

@warn.error
async def warn_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(':warning: Missing argument')
    
    else:
        await ctx.send(':warning: An unknown exception has occured. This has been logged.')
        raise error

def setup(bot):
    global serverLogs
    global modLogs

    serverLogs = bot.get_channel(config.logChannel)
    modLogs = bot.get_channel(config.modChannel)

    bot.add_command(warn)
    logging.info('Moderation module loaded')
