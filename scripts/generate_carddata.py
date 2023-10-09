import csv
import json
import re
import sys

from unidecode import unidecode

def all_opponents_lose_lore( amount ):
    player_loses_lore = lambda x: f"/p{x + 1}s1-{ amount }"
    return f'/ps1+{ amount };' + ';'.join(map(player_loses_lore, range(9)))

def card_name( card ):
    return unidecode(f"{card['name']}{', ' + card['subtitle'] if card.get('subtitle') else ''}")

def on_play_effects( card ):
    effects = []
    on_play_effect = re.search(r'([A-Z !?]+) When you play this', card.get('rules_text'))

    if on_play_effect:
        effects.append( f'/s { on_play_effect.groups()[0] }' )
        id = card['culture_invariant_id']

        if id == 2:
            # Ariel, Spectacular Singer
            effects.append('/vpDeckpt4')
        elif id == 105:
            # Aladdin, Street Rat
            effects.append( f'{ all_opponents_lose_lore(1) }' )

    return f";{ ';'.join( effects ) }" if len(effects) > 0 else ''

def trigger_scripts( card ):
    scripts = []
    id = card['culture_invariant_id']

    if id == 3:
        # Cinderella, Gentle and Kind
        scripts.append( f'<s><l>A WONDERFUL DREAM</l><f>/s A WONDERFUL DREAM;/cr90</f></s>')

    return ''.join(scripts)


def generate_scripts(card):
    scripts = [ f"<s><a>y</a><l>[Init]</l><f>/c1;/s { card_name( card ) }</f></s>" ]

    cost = card.get('ink_cost')

    if card.get('type') == 'Character':
        # Play
        scripts.append( f"<s><l>Play</l><f>/c1;/c3;/ps2-{cost};/ccblue={ card.get( 'strength' ) };/ccyellow={ card.get( 'willpower' ) }{ on_play_effects( card )}</f></s>" )

        # Shift
        shift = re.search(r'Shift ([0-9]) \(You may pay', card.get('rules_text'))
        if ( shift ):
            scripts.append(f"<s><l>Shift { shift.groups()[0] }</l><f>/c1;/c3;/ps2-{ shift.groups()[0] };/ccblue={ card.get( 'strength' ) };/ccyellow={ card.get( 'willpower' ) }{ on_play_effects( card )}</f></s>")

        # Quest
        result = card.get('quest_value')
        scripts.append( f"<s><l>Quest</l><f>/s { card_name( card ) } goes Questing, for { result } Lore;/c3;/ps1+{ result }</f></s>" )

    if card.get('type') == 'Item':
        # Cost
        scripts.append( f"<s><l>Play</l><f>/c1;/ps2-{cost}</f></s>" )

    if card.get('type') == 'Action':
        # Cost
        scripts.append( f"<s><l>Play</l><f>/c1;/ps2-{cost}</f></s>" )

        # Sing
        if 'Song' in card.get('subtypes', []):
            scripts.append( f"<s><l>Sing</l><f>/c1</f></s>" )

    if card.get('ink_convertible'):
        scripts.append( f"<s><l>Send to Inkwell</l><f>/s { card_name( card ) } goes to your Inkwell;/cf;/c1;/ccwhite=1</f></s>" )
        scripts.append( f"<s><l>Exert for Ink</l><f>/s You gain 1 Ink;/c3;/ps2+1</f></s>" )

    scripts.append( trigger_scripts( card ) )

    return ''.join( scripts )


if __name__ == "__main__":
    args = sys.argv[1:]

    csv.register_dialect('lackey', delimiter='\t', quoting=csv.QUOTE_MINIMAL, quotechar='"')

    with open(f"../data/en/catalog.json", 'r') as f:
        en_catalog = json.load(f)
        en_cards = []
        en_cards += [dict(item, **{'type': 'Character'}) for item in en_catalog['cards']['characters']]
        en_cards += [dict(item, **{'type': 'Item'}) for item in en_catalog['cards']['items']]
        en_cards += [dict(item, **{'type': 'Action'}) for item in en_catalog['cards']['actions']]
        en_cards = sorted(en_cards, key=lambda x: x['culture_invariant_id'])

    with open(f"../data/{args[0]}/catalog.json", 'r') as f:
        catalog = json.load(f)
        cards = []
        cards += [dict(item, **{'type': 'Character'}) for item in catalog['cards']['characters']]
        cards += [dict(item, **{'type': 'Item'}) for item in catalog['cards']['items']]
        cards += [dict(item, **{'type': 'Action'}) for item in catalog['cards']['actions']]
        cards = sorted(cards, key=lambda x: x['culture_invariant_id'])

    with open(f"../data/{args[0]}/carddata.txt", "w") as f:
        fieldnames = [
            'Name',
            'Set',
            'ImageFile'
        ]
        if args[0] != 'en':
            fieldnames.append('Name ' + args[0].upper())
        fieldnames = fieldnames + [
            'Type',
            'Subtypes',
            'Rarity',
            'Color',
            'Cost',
            'Inkwell',
            'Strength',
            'Willpower',
            'Quest',
            'Abilities',
            'Identifier',
            'Rules',
            'Flavor',
            'Number',
            'Artist',
            'Script'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect="lackey")

        writer.writeheader()
        for card in cards:
            data = {
                'Name': unidecode(f"{card['name']}{', ' + card['subtitle'] if card.get('subtitle') else ''}"),
                'Set': card['expansion_number'],
                'ImageFile': card['image_urls'][0]['url'].split('/')[-1].split('.')[0],
                'Type': card.get('type'),
                'Subtypes': unidecode(", ".join(card.get('subtypes', []))),
                'Rarity': card.get('rarity'),
                'Color': card.get('magic_ink_color'),
                'Cost': card.get('ink_cost'),
                'Inkwell': card.get('ink_convertible'),
                'Strength': card.get('strength'),
                'Willpower': card.get('willpower'),
                'Quest': card.get('quest_value'),
                'Abilities': unidecode(", ".join(card.get('abilities', []))),
                'Identifier': card.get('card_identifier'),
                'Rules': unidecode(card.get('rules_text').replace(' ', ' ')),
                'Flavor': unidecode(card.get('flavor_text').replace(' ', ' ')),
                'Number': f"{ card.get('culture_invariant_id') }".zfill(3),
                'Artist': unidecode(card.get('author', '').replace(' ', ' ').replace('\n', '')),
                'Script': generate_scripts(card)
            }
            if args[0] != 'en':
                en_card = next((x for x in en_cards if x['culture_invariant_id'] == card.get('culture_invariant_id')),
                               None)
                data['Name'] = unidecode(
                    f"{en_card['name']}{', ' + en_card['subtitle'] if en_card.get('subtitle') else ''}")

                fieldname = 'Name ' + args[0].upper()
                data[fieldname] = unidecode(f"{card['name']}{', ' + card['subtitle'] if card.get('subtitle') else ''}")

            writer.writerow(data)
