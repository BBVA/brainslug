import pkg_resources
import colorama

__all__ = ['BANNER']

P = colorama.Fore.MAGENTA + colorama.Style.BRIGHT
G = colorama.Fore.GREEN + colorama.Style.NORMAL
R = colorama.Style.RESET_ALL
W = colorama.Fore.WHITE + colorama.Style.NORMAL

distribution = pkg_resources.get_distribution('brainslug')
version = f'v{distribution.version}'

BANNER = (f"""
{P}  ______            __      {G} _______ __
{P} |   __ .----.---.-|__.-----{G}|     __|  .--.--.-----.
{P} |   __ |   _|  _  |  |     {G}|__     |  |  |  |  _  |
{P} |______|__| |___._|__|__|__{G}|_______|__|_____|___  |"""
                        f"{W}\n{version: >42}{G}   |_____|{R}").strip()
