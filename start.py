from config import load_config
from Auth import Authentication
import requests
from Thing import Thing

from monitor import Monitor


from pprint import pprint

conf = load_config()
lang = conf['lang']
base_url = conf['base_url']






def input_group(groups):
    group_selection_message = {
        'spa': 'Seleccione grupo: ',
        'eng': 'Select group: '
    }

    group_ids = []
    for group in groups:
        group_ids.append(group['id'])
        print(str(group['id']) + ' .- ' + str(group['name']) )
    selection = 0
    right_selection = False
    while not right_selection:
        selection = input(group_selection_message[lang])
        try:
            selection = int(selection)
        except Exception:
            continue
        pprint(selection)
        right_selection = True
        if not selection in group_ids:
            right_selection = False              
    return selection


def prompt_thing_info():
    not_registered_machine_message = {
        'spa': 'Este equipo no esta registrado en ninguno de sus grupos',
        'eng': 'This equipment is not registered in any of your groups'
    }
    register_confirmation_message = {
        'spa':'Desea registrarlo? (s/n): ',
        'eng': 'Would you like to register it? (y/n): '
    }
    enter_name_message = {
        'spa': 'Ingrese el nombre del equipo: ',
        'eng': "Enter equipment's name: "
    }
    name_confirmation_message = {
        'spa': 'le gusta? (s/n): ',
        'eng': 'do you like it? (y/n): '
    }
    this_is_the_name_message = {
        'spa': 'Este es el nombre: ',
        'eng': 'This is the name: '
    }
    equipment_successful_message = {
        'spa': 'Equipo registrado satisfactoriamente',
        'eng': 'Equipment sucessfully registered'
    }
    equipment_register_error = {
        'spa': 'No se pudo registrar el equipo',
        'eng': 'Equipment could not be registered'
    }

    print(not_registered_machine_message[lang])
    
    confirmation = ''
    while not confirmation.strip() in ['y', 's', 'n']:
        confirmation = input(register_confirmation_message[lang])
    if confirmation == 'n':
        quit()
    confirmation = ''
    while not confirmation.strip() in ['y', 's', 'n']:
        thing_name = input(enter_name_message[lang])
        print(this_is_the_name_message[lang] + thing_name)
        confirmation = input(name_confirmation_message[lang])
    thing.name = thing_name
    groups_ids = input_group(groups)
    thing.group = groups_ids
    pprint(thing.__dict__)
    response = thing.register()
    if 'status_code' in response and response.status_code == 200 or 201:
        print(equipment_successful_message[lang])
        pprint(response.json())
    else:
        print(equipment_register_error[lang])


"""This is where it begins"""

auth = Authentication()

if not auth.is_auth:
    quit()

thing = Thing()

print('ip: ' + str(thing.ip))
print('macs: ' + str(thing.macs))

groups = auth.getAdminGroups()

pprint(groups)
allThings = []
for group in groups:
    res = requests.get(base_url+'/group', params={'id': group['id']})
    group = res.json()
    #pprint(group)
    for t in group['things']:
        allThings.append(t)

found = thing.find_self(allThings)


if not found:
    prompt_thing_info()


m = Monitor(found['id'])
m.start()