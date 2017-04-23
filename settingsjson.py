import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Base title'},
    {'type': 'numeric',
     'title': 'Startup volume',
     'desc': 'Default volume at boot',
     'section': 'Base',
     'key': 'startupvolume'},
    {'type': 'path',
     'title': 'Media path',
     'desc': 'Path to the music directory',
     'section': 'Base',
     'key': 'mediapath'},
    {'type': 'bool',
     'title': 'Scan sub-folders',
     'desc': 'Scan sub-folders to laod medias',
     'section': 'Base',
     'key': 'boolsub_folders'},
    {'type': 'options',
     'title': 'Base lamp',
     'desc': 'Behaviour of the base lamp',
     'section': 'Base',
     'key': 'baselamp',
     'options': ['off', 'always on', 'only on alarm']},
    {'type': 'colorpicker',
     'title': 'Color of the lamp',
     'desc': 'Color of the lamp',
     'section': 'Base',
     'key': 'runcolor'},

    # {'type': 'string',
    #  'title': 'A string setting',
    #  'desc': 'String description text',
    #  'section': 'Base',
    #  'key': 'stringexample'},
])

