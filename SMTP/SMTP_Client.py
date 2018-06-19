import os.path
import configparser
from Template import Template


def parse_config(cfg_name='config.ini', dirname='Attachments'):
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.join(dirname, cfg_name))
    addressees = list(config['Addressees'])
    theme = config['Settings']['Theme']
    text_path = os.path.join(dirname, config['Settings']['Text'])
    files = []
    for filename in config['Files']:
        files.append(os.path.join(dirname, filename))
    return addressees, theme, files, text_path


def main():
    addressees, theme, files, text_path = parse_config()
    letter_template = Template(text_path, files, theme)
    for addressee in addressees:
        letter_template.send_to(addressee)


if __name__ == '__main__':
    main()
