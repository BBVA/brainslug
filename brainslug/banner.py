import pkg_resources


def generate_banner():
    distribution = pkg_resources.get_distribution('brainslug')
    version = f'v{distribution.version}'
    return (f"""
  ______            __       _______ __
 |   __ .----.---.-|__.-----|     __|  .--.--.-----.
 |   __ |   _|  _  |  |     |__     |  |  |  |  _  |
 |______|__| |___._|__|__|__|_______|__|_____|___  |"""
            f"            \n{version: >42}   |_____|")
