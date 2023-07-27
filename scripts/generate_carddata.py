import csv
import json
import sys


def add_type(x, type):
    x.update(type=type)
    return x


if __name__ == "__main__":
    args = sys.argv[1:]

    csv.register_dialect('lackey', delimiter='\t', quoting=csv.QUOTE_MINIMAL, quotechar="'")

    with open( f"../data/{ args[0] }/catalog.json", 'r') as f:
        catalog = json.load(f)
        cards = []
        cards += [dict(item, **{'type': 'Character'}) for item in catalog['cards']['characters']]
        cards += [dict(item, **{'type': 'Item'}) for item in catalog['cards']['items']]
        cards += [dict(item, **{'type': 'Action'}) for item in catalog['cards']['actions']]
        cards = sorted(cards, key=lambda x: x['culture_invariant_id'])

    with open(f"../data/{ args[0]}/carddata.txt", "w") as f:
        fieldnames = [
            'Name',
            'Set',
            'ImageFile',
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
            'Artist'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, dialect="lackey")

        writer.writeheader()
        for card in cards:
            writer.writerow({
                'Name': f"{ card['name'] }{ ', ' + card['subtitle'] if card.get('subtitle') else ''}",
                'Set': card['expansion_number'],
                'ImageFile': card['image_urls'][0]['url'].split('/')[-1].split('.')[0],
                'Type': card.get('type'),
                'Subtypes': json.dumps(card.get('subtypes', [])),
                'Rarity': card.get('rarity'),
                'Color': card.get('magic_ink_color'),
                'Cost': card.get('ink_cost'),
                'Inkwell': card.get('ink_convertible'),
                'Strength': card.get('strength'),
                'Willpower': card.get('willpower'),
                'Quest': card.get('quest_value'),
                'Abilities': json.dumps(card.get('abilities', [])),
                'Identifier': card.get('card_identifier'),
                'Rules': card.get('rules_text').replace(' ', ' '),
                'Flavor': card.get('flavor_text').replace(' ', ' '),
                'Number': card.get('culture_invariant_id'),
                'Artist': card.get('author', '').replace(' ', ' ').replace('\n', '')
            })
