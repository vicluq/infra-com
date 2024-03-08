reservations: dict[str, str] = {
      'E401-ter-12h': 'localhost:8877',
      'E401-ter-13h': 'localhost:8877',
      'E401-ter-17h': 'localhost:8877',
}

hour = '8h'
day = 'sex'
room = 'E301'
key = 'localhost:8877'

def _check_available_hours(room, day) -> list[str]:
            hours = [f'{h}h' for h in list(range(8, 18))]
            occupied = [k.split('-')[-1] for k in list(reservations.keys()) 
                        if k.split('-')[0] == room and k.split('-')[1] == day]

            return [h for h in hours if h not in occupied]

msg = ' '.join(_check_available_hours(room, day))
msg = f'{room} {day} -> {msg}'.encode()
print(msg)