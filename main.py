#!/usr/bin/env python3

import sys
import random
import csv
import json
import genanki

## Define external resource paths
jmdict_path = './resources/external/jmdict-eng-common-3.5.0.json'
kanjidic2_path = './resources/external/kanjidic2-en-3.5.0.json'
kanji_database_path = './resources/external/kanji_database.csv'

if __name__ == '__main__':

    ## Read format/style resources to strings
    with open('./resources/qfmt.html', newline='') as f:
        kanji_qfmt = f.read()
    with open('./resources/afmt.html', newline='') as f:
        kanji_afmt = f.read()
    with open('./resources/style.css', newline='') as f:
        kanji_style = f.read()

    ## Create deck
    kanji_deck = genanki.Deck(
        1360154107,
        'Jouyou Kanji',
    )

    ## Create note model
    kanji_model = genanki.Model(
        1827794720,
        'Jouyou Kanji',
        fields = [
            {'name': 'id'},
            {'name': 'Kanji'},
            {'name': 'Index'},
            {'name': 'On Reading'},
            {'name': 'Kun Reading'},
            {'name': 'Meaning'},
            {'name': 'Example'},
            {'name': 'Classification'},
            {'name': 'Radical'},
            {'name': 'Grade'},
            {'name': 'JLPT'},
            {'name': 'Strokes'},
            {'name': 'Frequency'},
        ],
        templates = [
            {
                'name': 'Jouyou Kanji',
                'qfmt': kanji_qfmt,
                'afmt': kanji_afmt,
            },
        ],
        css = kanji_style,
        sort_field_index = 2,
    )

    ## Generate guid based on databse id and kanji
    class KanjiNote(genanki.Note):
        @property
        def guid(self):
            return genanki.guid_for(self.fields[0], self.fields[1])

    ## Read external resources to dictionaries
    with open(jmdict_path, newline='') as f:
        jmdict = json.load(f)
    with open(kanjidic2_path, newline='') as f:
        kanjidic2 = json.load(f)

    with open(kanji_database_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
        kanji_database = sorted(reader, reverse = True,
                                key = lambda row:
                                int(row['Kanji Frequency without Proper Nouns']))

    ## Loop through database rows
    for idx, row in enumerate(kanji_database):
        search_kanji = row['Kanji']

        ## Find words containing search kanji
        word_list = []
        for word in jmdict['words']:
            if (word['kanji']):
                kanji = word['kanji'][0]
                if (kanji['common'] and search_kanji in kanji['text']):
                    kanji_t = kanji['text']
                    kana_t = word['kana'][0]['text']
                    word_list.append(f'{kanji_t}[{kana_t}]')
        random.shuffle(word_list)

        ## Find readings/meanings of serach kanji
        reading_list_on = []
        reading_list_kun = []
        meaning_list = []
        for character in kanjidic2['characters']:
            kanji = character['literal']
            readings = character['readingMeaning']['groups'][0]['readings']
            meanings = character['readingMeaning']['groups'][0]['meanings']
            if (kanji == search_kanji):
                for reading in readings:
                    if (reading['type'] == 'ja_on'):
                        reading_list_on.append(reading['value'])
                    elif (reading['type'] == 'ja_kun'):
                        reading_list_kun.append(reading['value'])

                for meaning in meanings:
                    if (meaning['lang'] == 'en'):
                        meaning_list.append(meaning['value'])


        ## Add JLPT level as tag
        tag_list = []
        jlpt = row['JLPT-test']
        if (int(jlpt)):
            tag_list.append(f'jlpt_n{jlpt}')

        ## Add note to deck
        note_id = row['id']
        note_index = str(idx + 1)
        kanji_deck.add_note(KanjiNote(
            model = kanji_model,
            fields = [
                note_id,
                search_kanji,
                note_index,
                ', '.join(reading_list_on[:3]),
                ', '.join(reading_list_kun[:3]),
                '; '.join(meaning_list[:3]),
                ',  '.join(word_list[:3]),
                row['Kanji Classification'],
                row['Name of Radical'],
                row['Grade'],
                row['JLPT-test'],
                row['Strokes'],
                row['Kanji Frequency without Proper Nouns'],
            ],
            tags = tag_list,
        ))

        print(f'Added note with id {note_id}, index {note_index}')

    ## Write to apkg file and finish up
    genanki.Package(kanji_deck).write_to_file('out.apkg')
    print('Finished successfully. Wrote deck to out.apkg')
    sys.exit(0)
